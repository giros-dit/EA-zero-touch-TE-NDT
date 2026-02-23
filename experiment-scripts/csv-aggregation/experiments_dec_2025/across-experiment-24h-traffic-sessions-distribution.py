import matplotlib.pyplot as plt

# Hours of the day (1–24)
hours = list(range(1, 25))

# Number of user traffic sessions per hour
sessions = [
    6, 5, 4, 3, 3, 4, 5, 6,
    7, 8, 8, 8, 8, 8, 8, 8,
    8, 9, 9, 9, 10, 10, 9, 8
]

# Increase figure size to improve readability
#plt.figure(figsize=(12, 5))
plt.figure(figsize=(16,8))

# Bar chart with light gray color
plt.bar(hours, sessions, width=0.6, color='lightgray', edgecolor='black')  # borde negro opcional

# Axis labels with bigger font
plt.xlabel("Hour of the day", fontsize=23)
plt.ylabel("Number of traffic sessions", fontsize=23)

# Title with bigger font
#plt.title("Distribution of traffic sessions over 24 hours", fontsize=26)

# Show all ticks on both axes with bigger font
plt.xticks(hours, fontsize=22)
plt.yticks(range(0, max(sessions) + 1, 1), fontsize=22)

plt.tight_layout()
plt.savefig("graphics/across-experiment-24h-traffic-sessions-distribution.png", dpi=300)
plt.close()