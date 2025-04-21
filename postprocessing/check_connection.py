from clip_client import Client
import argparse
import sys
import time


def parse_args():
    parser = argparse.ArgumentParser(description="Test CLIP server connection")
    parser.add_argument("--protocol", type=str, default="GRPC", help="Protocol used by the server")
    parser.add_argument("--local-addr", type=str, help="Local server address")
    parser.add_argument("--private-addr", type=str, help="Private server address")
    parser.add_argument("--public-addr", type=str, help="Public server address")
    return parser.parse_args()


def print_connection_info(protocol: str, addresses: dict):
    print("╭────────────── 🔗 Connection Test ───────────────╮")
    print(f"│  ⛓      {'Protocol'.ljust(10)} {protocol.ljust(30)} ")
    for name, addr in addresses.items():
        icon = "🏠" if name == "local" else "🔒" if name == "private" else "🌍"
        status = f"{addr if addr else 'Not provided'}"
        name_padded = f"{name.capitalize()}".ljust(10)
        print(f"│  {icon}     {name_padded} {status.ljust(30)} ")
    print("╰─────────────────────────────────────────────────╯")


def test_connection(protocol: str, addresses: dict) -> bool:
    successful_connections = {"local": False, "private": False, "public": False}
    client = None
    for name, addr in addresses.items():
        name: str
        addr: str
        if not addr:
            continue

        addr = (
            f"{protocol.lower()}://{addr}"
            if not addr.startswith(("grpc://", "http://", "https://"))
            else addr
        )

        if name == "local":
            addr_for_health_check = addr

        print(f"\nTesting connection to {name} address: {addr}")
        try:
            client = Client(addr)
            client.profile()  # Verify connection
            print(f"✅ Successfully connected to {name} address")
            successful_connections[name] = True
        except Exception as e:
            print(f"❌ Failed to connect to {name} address: {str(e)}")

    # Return True if both local and private connections succeeded, regardless of public
    if successful_connections["local"] and successful_connections["private"]:
        return True, addr_for_health_check, client
    elif (
        successful_connections["local"]
        or successful_connections["private"]
        or successful_connections["public"]
    ):
        # Return True if at least one connection succeeded
        return True, addr_for_health_check, client
    else:
        # Return False if all connections failed
        return False, None, None


def main():
    args = parse_args()

    protocol = args.protocol
    addresses = {"local": args.local_addr, "private": args.private_addr, "public": args.public_addr}

    print_connection_info(protocol, addresses)
    success, addr, client = test_connection(protocol, addresses)

    if not success:
        print("\n⛔ Could not connect to any CLIP server address. Application will exit.")
        sys.exit(1)
    else:
        print("\n🔥 CLIP server connection test completed. Application will continue running.")

    printed = False
    while True:
        if addr is None and not printed:
            print("👽 No address for health check. Will work until server went down.")
            printed = True
        elif addr is None and printed:
            time.sleep(600)
            print("⚙️ Still working in the background...")
        else:
            if client:
                print("\n⏳ 600 seconds until next health check...")
                time.sleep(600)
            else:
                client = Client(addr)
            client.profile()


if __name__ == "__main__":
    main()
