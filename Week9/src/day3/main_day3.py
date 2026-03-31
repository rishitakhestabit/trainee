import asyncio
from orchestrator.orchestrator import Orchestrator

async def main():
    orch = Orchestrator()
    print("Agentic Data Assistant - type 'exit' to quit\n")
    while True:
        try:
            q = input("You: ").strip()
            if not q or q.lower() in ("exit", "quit"):
                break
            res = await orch.run(q)
            print(f"\n{res}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())