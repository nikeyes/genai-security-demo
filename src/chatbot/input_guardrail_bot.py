import torch
from torch.nn.functional import softmax
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

class InputGuardrailsBot:
    def __init__(self, llm):
        prompt_injection_model_name = 'meta-llama/Prompt-Guard-86M'
        self.tokenizer = AutoTokenizer.from_pretrained(prompt_injection_model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(prompt_injection_model_name)
        self.llm = llm
        self.system_prompt = ""

    def chat(self, user_prompt: str):
        jailbreak_score = self.get_jailbreak_score(user_prompt)
        indirect_injection_score = self.get_indirect_injection_score(user_prompt)
        if jailbreak_score > 0.9 or indirect_injection_score > 0.9:
            return f"""
    ⚠️ Security Alert
    {'=' * 40}
    🚫 Attack Attempt Detected
    {'‾' * 40}
    • Jailbreak Score: {jailbreak_score*100:.1f}%
    • Indirect Injection Score: {indirect_injection_score*100:.1f}%
    • Status: Blocked
    • Action Required: Please rephrase your input
    """

        llm_response = self.llm.invoke(self.system_prompt, user_prompt)
        return f"""
    ✅🔒 Security Check Passed
    {'=' * 40}
    • Jailbreak Score: {jailbreak_score*100:.1f}%
    • Indirect Injection Score: {indirect_injection_score*100:.1f}%
    • Status: Allowed
    {'‾' * 40}

    {llm_response}
    """

    def get_class_probabilities(self, text, temperature=1.0, device='cpu'):
        """
        Evaluate the model on the given text with temperature-adjusted softmax.
        
        Args:
            text (str): The input text to classify.
            temperature (float): The temperature for the softmax function. Default is 1.0.
            device (str): The device to evaluate the model on.
         
        Returns:
            torch.Tensor: The probability of each class adjusted by the temperature.
        """
        # Encode the text
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = inputs.to(device)
        # Get logits from the model
        with torch.no_grad():
            logits = self.model(**inputs).logits
        # Apply temperature scaling
        scaled_logits = logits / temperature
        # Apply softmax to get probabilities
        probabilities = softmax(scaled_logits, dim=-1)
        return probabilities

    def get_jailbreak_score(self, text, temperature=1.0, device='cpu'):
        """
        Evaluate the probability that a given string contains malicious jailbreak or prompt injection.
        Appropriate for filtering dialogue between a user and an LLM.
        
        Args:
            text (str): The input text to evaluate.
            temperature (float): The temperature for the softmax function. Default is 1.0.
            device (str): The device to evaluate the model on.
            
        Returns:
            float: The probability of the text containing malicious content.
        """
        probabilities = self.get_class_probabilities(text, temperature, device)
        return probabilities[0, 2].item()
    
    def get_indirect_injection_score(self, text, temperature=1.0, device='cpu'):
        """
        Evaluate the probability that a given string contains any embedded instructions (malicious or benign).
        Appropriate for filtering third party inputs (e.g. web searches, tool outputs) into an LLM.
        
        Args:
            text (str): The input text to evaluate.
            temperature (float): The temperature for the softmax function. Default is 1.0.
            device (str): The device to evaluate the model on.
            
        Returns:
            float: The combined probability of the text containing malicious or embedded instructions.
        """
        probabilities = self.get_class_probabilities(text, temperature, device)
        return (probabilities[0, 1] + probabilities[0, 2]).item()
