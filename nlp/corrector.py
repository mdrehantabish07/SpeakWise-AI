from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


MODEL_NAME = "vennify/t5-base-grammar-correction"

print("Loading grammar correction model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

print("Model loaded successfully!")


def correct_sentence(sentence):

    input_text = "grammar: " + sentence

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=128,
        truncation=True
    )

    outputs = model.generate(
        **inputs,
        max_length=128,
        num_beams=4,
        early_stopping=True
    )

    corrected = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return corrected


# ==================================
# TEST
# ==================================

print("\nSpeakWise Grammar Corrector")
print("---------------------------")

sentence = input("Enter an English sentence: ")

corrected = correct_sentence(sentence)

print("\nOriginal:")
print(sentence)

print("\nCorrected:")
print(corrected)