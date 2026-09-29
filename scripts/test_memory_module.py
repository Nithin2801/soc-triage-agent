from backend.app.memory import recall_experience


query = """
SOC alert investigation.

A medium-severity encoded PowerShell alert occurred on BKP-SRV-02
using the svc-veeam service account.

The process was launched by Veeam.Backup.Service.exe at approximately
02:05 during the scheduled backup window.

What previous analyst experience is relevant?
What conditions were required for the previous Likely Benign decision?
"""


print("APPLICATION MEMORY MODULE TEST")
print("------------------------------")
print()
print("Query:")
print(query.strip())
print()
print("Recalled memories:")

memories = recall_experience(query)

if not memories:
    print("No memories returned.")
else:
    for index, memory in enumerate(memories, start=1):
        print()
        print(f"[Memory {index}]")
        print(f"Type: {memory['type']}")
        print(f"Text: {memory['text']}")

print()
print("MEMORY MODULE TEST PASSED")