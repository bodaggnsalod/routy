import requests
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import networkx as nx

# ============================================================
# 1. Live-Verkehrsdaten holen (Autobahn API)
# ============================================================

def get_live_traffic_delay():
    """
    Holt Live-Verkehrsstörungen von der Autobahn API.
    Gibt einen Verzögerungsfaktor zurück (0.0 = kein Delay, 1.0 = stark).
    """
    try:
        url = "https://verkehr.autobahn.api.bund.dev/v3/events"
        r = requests.get(url, timeout=5)
        events = r.json().get("events", [])

        # Delay proportional zur Anzahl der Meldungen
        delay_factor = min(1.0, len(events) / 50.0)
        print(f"[Live Traffic Delay Factor] {delay_factor}")
        return delay_factor

    except Exception as e:
        print("Fehler beim Abruf der Live-Daten:", e)
        return 0.0


# ============================================================
# 2. Einfaches Straßennetz (synthetisches Beispiel)
# ============================================================

def build_graph():
    G = nx.Graph()

    # Beispiel-Knoten
    nodes = ['A', 'B', 'C', 'D', 'E']
    for n in nodes:
        G.add_node(n)

    # Beispiel-Kanten (mit Basis-Reisezeiten)
    edges = [
        ('A', 'B', 5),
        ('B', 'C', 3),
        ('A', 'D', 4),
        ('D', 'E', 2),
        ('E', 'C', 4)
    ]

    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    return G


# ============================================================
# 3. RL-Environment
# ============================================================

class TrafficEnv:
    def __init__(self):
        self.G = build_graph()
        self.nodes = list(self.G.nodes())
        self.start = 'A'
        self.goal = 'C'
        self.reset()

    def reset(self):
        self.current = self.start
        return self.state()

    def state(self):
        """
        Rückgabe: One-Hot Knotenposition + Distanz zum Ziel
        """
        one_hot = np.zeros(len(self.nodes))
        idx = self.nodes.index(self.current)
        one_hot[idx] = 1

        dist = nx.shortest_path_length(self.G, self.current, self.goal)

        return np.concatenate([one_hot, [dist]])

    def step(self, action):
        """
        Aktion = Index des nächsten Knotens in self.nodes
        """
        next_node = self.nodes[action]

        if not self.G.has_edge(self.current, next_node):
            # Illegale Aktion → harte Strafe
            return self.state(), -10, False

        traffic_delay = get_live_traffic_delay()

        base_cost = self.G[self.current][next_node]['weight']
        cost = base_cost * (1 + traffic_delay)

        reward = -cost

        self.current = next_node

        done = self.current == self.goal
        if done:
            reward += 20  # Bonus für Zielerreichung

        return self.state(), reward, done


# ============================================================
# 4. DQN-Modell
# ============================================================

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        return self.net(x)


# ============================================================
# 5. Training Loop
# ============================================================

def train_agent(episodes=20):
    env = TrafficEnv()

    input_dim = len(env.state())
    output_dim = len(env.nodes)

    model = DQN(input_dim, output_dim)
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()

    gamma = 0.9
    epsilon = 0.2

    for ep in range(episodes):
        state = env.reset()
        total_reward = 0

        for t in range(20):  # max steps
            s = torch.tensor(state, dtype=torch.float32)

            # ε-greedy Policy
            if random.random() < epsilon:
                action = random.randint(0, output_dim - 1)
            else:
                with torch.no_grad():
                    action = model(s).argmax().item()

            next_state, reward, done = env.step(action)
            total_reward += reward

            # Q-Learning Update
            q_values = model(s)
            next_q_values = model(torch.tensor(next_state, dtype=torch.float32))

            target = q_values.clone()
            target[action] = reward + gamma * next_q_values.max().item()

            loss = loss_fn(q_values, target.detach())

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            state = next_state

            if done:
                break

        print(f"Episode {ep+1}/{episodes} | Reward: {total_reward:.2f}")

    torch.save(model.state_dict(), "dqn_traffic_model.pth")
    print("\nModell gespeichert als dqn_traffic_model.pth")

    return model


# ============================================================
# Start Training
# ============================================================

if __name__ == "__main__":
    train_agent(episodes=10)
