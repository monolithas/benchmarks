import toml

def configuration(path: str) -> dict | None:
    with open(path, 'r') as f:
        return toml.loads(f.read(), _dict=dict)

def run():
    config = configuration('benchmarks.toml')
    print(config)