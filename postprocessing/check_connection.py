from clip_client import Client
import argparse
import sys


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
        print(f"\nTesting connection to {name} address: {addr}")
        try:
            client = Client(addr)
            server_info = client.profile()  # Verify connection
            print(f"✅ Successfully connected to {name} address")
            print(f"   Server info: {server_info}")
            successful_connections[name] = True
        except Exception as e:
            print(f"❌ Failed to connect to {name} address: {str(e)}")

    # Return True if both local and private connections succeeded, regardless of public
    if successful_connections["local"] and successful_connections["private"]:
        return True
    elif (
        successful_connections["local"]
        or successful_connections["private"]
        or successful_connections["public"]
    ):
        # Return True if at least one connection succeeded
        return True
    else:
        # Return False if all connections failed
        return False


def main():
    args = parse_args()

    protocol = args.protocol
    addresses = {"local": args.local_addr, "private": args.private_addr, "public": args.public_addr}

    print_connection_info(protocol, addresses)
    success = test_connection(protocol, addresses)

    if not success:
        print("\nCould not connect to any CLIP server address")
        sys.exit(1)
    else:
        print("\nCLIP server connection test completed successfully")


if __name__ == "__main__":
    main()
