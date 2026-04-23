from pathlib import Path

from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialCreator

# Set up connection to auto_code API.
# Only set dev=True if you have access to a local development server.
# The API class looks for an environment variable named AUTOCODE_API_TOKEN_DEV or AUTOCODE_API_TOKEN_PROD.
# This example fetches trial metadata first, then downloads protocol bytes from
# GET /api/trial/<id>/protocol/ via trial_manager.get_protocol_file().
dev_flag = False
trial_id = 20  # use trial 17 for dev, trial 20 for prod
download_protocol = False

api = AutoCodeAPI(dev=dev_flag)
trial_manager = TrialCreator(api, trial_id=trial_id)

trial_metadata = trial_manager.get_trial_metadata()

print("Trial metadata:")
print(f"  id: {trial_metadata.id}")
print(f"  acronym: {trial_metadata.acronym}")
print(f"  title: {trial_metadata.title}")
print(f"  has_protocol: {trial_metadata.has_protocol}")
print(f"  protocol_filename: {trial_metadata.protocol_filename}")
print(f"  protocol_download_url: {trial_metadata.protocol_download_url}")

protocol_bytes, protocol_filename = trial_manager.get_protocol_file()

if protocol_bytes is None:
    print("\nNo protocol is available for this trial.")
else:
    print("\nProtocol download succeeded.")
    print(f"  filename: {protocol_filename}")
    print(f"  bytes downloaded: {len(protocol_bytes)}")
    print(f"  bytes endpoint used: trial/{trial_id}/protocol/")

    if download_protocol:
        output_dir = Path("Generated Code") / "Downloaded Protocols"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_filename = protocol_filename or f"trial_{trial_id}_protocol.bin"
        output_path = output_dir / output_filename
        output_path.write_bytes(protocol_bytes)

        print(f"Saved protocol to: {output_path}")
