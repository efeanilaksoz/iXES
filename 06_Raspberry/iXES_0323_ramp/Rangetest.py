
Low = 330
High = 80
StimRange = [Low, High]
print("Lower bound = ", Low, "and Higher bound = ", High)

angle = 340
print("Actual angle is = ", angle)

if angle in range(Low, High):
    print("Stimulation is ON")
else:
    print("Stimulation is OFF")
