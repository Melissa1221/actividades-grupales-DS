import json
import uuid

def main():
    deployment_id = str(uuid.uuid4())
    print(json.dumps({"deployment_id": deployment_id}))

if __name__ == "__main__":
    main()