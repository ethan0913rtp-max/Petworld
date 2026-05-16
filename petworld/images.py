def get_pet_image(species: str, variant: int) -> str:
    variant = max(1, min(50, variant or 1))
    base = SPECIES_IMAGES.get(species, SPECIES_IMAGES.get("cat", []))
    if not base:
        return ""
    return base[(variant - 1) % len(base)]

SPECIES_IMAGES = {
    "cat": [
        "https://cataas.com/cat?v=1","https://cataas.com/cat?v=2",
        "https://cataas.com/cat?v=3","https://cataas.com/cat?v=4",
        "https://cataas.com/cat?v=5","https://cataas.com/cat?v=6",
        "https://cataas.com/cat?v=7","https://cataas.com/cat?v=8",
        "https://cataas.com/cat?v=9","https://cataas.com/cat?v=10",
        "https://cataas.com/cat?v=11","https://cataas.com/cat?v=12",
        "https://cataas.com/cat?v=13","https://cataas.com/cat?v=14",
        "https://cataas.com/cat?v=15","https://cataas.com/cat?v=16",
        "https://cataas.com/cat?v=17","https://cataas.com/cat?v=18",
        "https://cataas.com/cat?v=19","https://cataas.com/cat?v=20",
        "https://cataas.com/cat?v=21","https://cataas.com/cat?v=22",
        "https://cataas.com/cat?v=23","https://cataas.com/cat?v=24",
        "https://cataas.com/cat?v=25","https://cataas.com/cat?v=26",
        "https://cataas.com/cat?v=27","https://cataas.com/cat?v=28",
        "https://cataas.com/cat?v=29","https://cataas.com/cat?v=30",
        "https://cataas.com/cat?v=31","https://cataas.com/cat?v=32",
        "https://cataas.com/cat?v=33","https://cataas.com/cat?v=34",
        "https://cataas.com/cat?v=35","https://cataas.com/cat?v=36",
        "https://cataas.com/cat?v=37","https://cataas.com/cat?v=38",
        "https://cataas.com/cat?v=39","https://cataas.com/cat?v=40",
        "https://cataas.com/cat?v=41","https://cataas.com/cat?v=42",
        "https://cataas.com/cat?v=43","https://cataas.com/cat?v=44",
        "https://cataas.com/cat?v=45","https://cataas.com/cat?v=46",
        "https://cataas.com/cat?v=47","https://cataas.com/cat?v=48",
        "https://cataas.com/cat?v=49","https://cataas.com/cat?v=50",
    ],
}

for _s in ["dog","bunny","hamster","fox","wolf","raccoon","deer","panda","koala","bear","tiger","lion","elephant","unicorn","cerberus","kitsune","kirin","parrot","penguin","crow","owl","flamingo","toucan","peacock","eagle","hummingbird","phoenix","griffin","dragon","lizard","chameleon","turtle","snake","crocodile","hydra","koi","clownfish","shark","jellyfish","axolotl","butterfly","firefly","bee","beetle","frog","salamander","toad","sprite","leviathan","thunderbird"]:
    if _s not in SPECIES_IMAGES:
        SPECIES_IMAGES[_s] = [f"https://cataas.com/cat?{_s}={i}" for i in range(1, 51)]
