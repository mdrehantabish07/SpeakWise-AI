from openhinglish import normalize


print("================================")
print("     HINGLISH NORMALIZER")
print("================================")

text = input("\nEnter Hinglish: ")

result = normalize(text)

print("\nOriginal:")
print(text)

print("\nHindi:")
print(result.display)

print("\nHindi for AI:")
print(result.tts)

print("\nConfidence:")
print(round(result.confidence, 2))