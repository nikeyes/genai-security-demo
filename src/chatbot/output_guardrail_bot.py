import asyncio
import os
from codeshield.cs import CodeShield
from config.token_usage import format_token_usage

os.environ['TOKENIZERS_PARALLELISM'] = 'false'


class OutputGuardrailsBot:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = ''

    def chat(self, user_prompt: str):
        result, usage = self.llm.invoke(self.system_prompt, user_prompt)
        summary = asyncio.run(self.scan_llm_output(result, usage))
        return summary

    async def scan_llm_output(self, llm_output_code, usage):
        result = await CodeShield.scan_code(llm_output_code)

        output = []
        output.append('\n🔍 Security Scan Results:')
        output.append('=' * 40)

        # Status section
        output.append(f'Status: {"⚠️ INSECURE" if result.is_insecure else "✅ SECURE"}')
        output.append(f'Recommended Action: {result.recommended_treatment.upper()}')

        # Issues section
        if result.issues_found:
            output.append('\n📋 Issues Found:')
            output.append('-' * 40)
            for issue in result.issues_found:
                output.append(f'\n• Issue Type: {issue.description}')
                output.append(f'  Severity: {issue.severity.value}')
                output.append(f'  CWE ID: {issue.cwe_id}')
                if issue.line:
                    output.append(f'  Line Number: {issue.line}')
                if issue.pattern_id:
                    output.append(f'  Pattern: {issue.pattern_id}')
            output.append('\n📝 LLM Response:')
            output.append('-' * 40)
            output.append(f'{llm_output_code}')
        else:
            output.append('\n✅ No security issues detected')
            output.append('\n📝 LLM Response:')
            output.append('-' * 40)
            output.append(f'{llm_output_code}')

        # Add token usage information
        output.append('\n' + format_token_usage(usage))

        formatted_output = '\n'.join(output)
        print(formatted_output)  # For debugging
        return formatted_output
