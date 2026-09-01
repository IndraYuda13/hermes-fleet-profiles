# Custom LLM Configuration (e.g., 9router)

To configure the self-hosted Firecrawl instance at `/tmp/firecrawl` to use a custom OpenAI-compatible AI provider (such as 9router):

1. Open `/tmp/firecrawl/.env`.
2. Add or update the following variables:
   ```env
   OPENAI_BASE_URL="https://api.9router.com/v1"
   OPENAI_API_KEY="your_api_key_here"
   ```
3. Apply the changes by restarting the containers:
   ```bash
   cd /tmp/firecrawl
   docker compose down && docker compose up -d
   ```

*Note: Firecrawl defaults to standard model names (like `gpt-4o`). Configure `LLM_MODEL` if the custom provider requires an exact model string.*