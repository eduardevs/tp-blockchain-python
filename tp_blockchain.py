import hashlib
import time


class Block:
    """
    Représente un bloc dans la blockchain.
    Contient les données, le hash du bloc précédent, le nonce, le timestamp, et son propre hash.
    """

    def __init__(self, data, previous_hash='', timestamp=None):
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calcule le hash SHA256 du bloc basé sur timestamp, données, previous_hash et nonce.
        """
        to_hash = f"{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(to_hash.encode()).hexdigest()

    def mine_block(self, difficulty):
        """
        Effectue un minage Proof of Work en cherchant un hash commençant par 'difficulty' zéros.
        """
        target = '0' * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def update_data(self, new_data):
        """
        Met à jour les données du bloc et recalcul le hash.
        """
        self.data = new_data
        self.nonce = 0
        self.hash = self.calculate_hash()

    def __repr__(self):
        return (f"Block(hash={self.hash[:10]}..., prev_hash={self.previous_hash[:10]}..., "
                f"nonce={self.nonce}, data={self.data}, ts={self.timestamp})")


class Blockchain:
    """
    Chaîne de blocs avec méthode pour ajouter des blocs, créer un bloc Genesis, etc.
    """

    def __init__(self, difficulty=3, genesis_timestamp=1000):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block(genesis_timestamp)]

    def create_genesis_block(self, timestamp):
        """
        Crée le bloc Genesis avec timestamp donné.
        """
        genesis = Block("Genesis Block", "0", timestamp)
        genesis.mine_block(self.difficulty)
        return genesis

    def add_block(self, data, timestamp=None):
        """
        Ajoute un nouveau bloc à la chaîne avec données et timestamp donné.
        """
        last_block = self.chain[-1]
        new_block = Block(data, last_block.hash, timestamp)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def is_chain_valid(self):
        """
        Vérifie l'intégrité de la blockchain en validant le hash et le previous_hash.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False, i
            if current.previous_hash != prev.hash:
                return False, i
            if not current.hash.startswith('0' * self.difficulty):
                return False, i
        return True, None


class MerkleTree:
    def __init__(self, leaves):
        """
        leaves: liste de hash (feuilles)
        """
        self.leaves = leaves[:]
        self.tree = []
        if leaves:
            self.build_tree()

    def build_tree(self):
        current_level = self.leaves[:]
        self.tree = [current_level]

        while len(current_level) > 1:
            if len(current_level) % 2 != 0:
                # Dupliquer le dernier si impair
                current_level.append(current_level[-1])

            next_level = []
            for i in range(0, len(current_level), 2):
                combined = current_level[i] + current_level[i+1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(new_hash)

            self.tree.append(next_level)
            current_level = next_level

    def compute_merkle_root(self):
        """Retourne la racine Merkle"""
        if not self.tree:
            return ''
        return self.tree[-1][0]

    def print_tree(self):
        print("*** Arbre de Merkle complet ***\n")
        for i, level in enumerate(self.tree):
            print(f"Niveau {i} ({len(level)} nœuds) :")
            for h in level:
                print(f"  {h}")
            print()


def compare_blockchains(bc1, bc2):
    """
    Compare deux blockchains bloc par bloc.
    """
    diffs = []
    for i, (b1, b2) in enumerate(zip(bc1.chain, bc2.chain)):
        if b1.hash != b2.hash:
            diffs.append(i)
    if not diffs:
        print("✅ Les blockchains sont identiques (blocs).")
    else:
        print("❌ Différences détectées dans les blocs :", diffs)


def compare_merkle_roots(bc1, bc2):
    hashes1 = [block.hash for block in bc1.chain]
    hashes2 = [block.hash for block in bc2.chain]

    tree1 = MerkleTree(hashes1)
    tree2 = MerkleTree(hashes2)

    root1 = tree1.compute_merkle_root()
    root2 = tree2.compute_merkle_root()

    print("\nArbre Merkle de la blockchain 1 :")
    tree1.print_tree()

    print("\nArbre Merkle de la blockchain 2 :")
    tree2.print_tree()

    print(f"Racine Merkle 1 : {root1}")
    print(f"Racine Merkle 2 : {root2}")

    if root1 == root2:
        print("✅ Les blockchains sont identiques (Merkle Root).")
    else:
        print("❌ Les blockchains diffèrent (Merkle Root).")
        compare_blockchains(bc1, bc2)


def simulate_decentralized_blockchains(num_instances=5, difficulty=3, num_blocks=4, genesis_timestamp=1000):
    """
    Simule plusieurs blockchains identiques avec les mêmes données et timestamps.
    Retourne la liste des instances Blockchain.
    """
    # Génère les timestamps fixes
    timestamps = [genesis_timestamp + i for i in range(1, num_blocks + 1)]

    # Initialise les blockchains identiques
    blockchains = [Blockchain(difficulty, genesis_timestamp=genesis_timestamp)
                   for _ in range(num_instances)]

    # Ajoute les mêmes blocs à chaque instance
    for i in range(num_blocks):
        data = f"Transaction {i}"
        ts = timestamps[i]
        for bc in blockchains:
            bc.add_block(data, timestamp=ts)

    return blockchains

# === TESTS ===


def test_creation_blockchain():
    print("\n\n🧪 === TEST 1 : création blockchain et chaînage des blocs === 🧪 \n")

    bc = Blockchain()
    bc.add_block("Bloc 1")
    bc.add_block("Bloc 2")

    # Vérifie que le premier bloc est le Genesis
    assert bc.chain[0].previous_hash == "0", "Le Genesis doit avoir previous_hash '0'"

    # Vérifie que chaque bloc pointe vers le hash du précédent
    for i in range(1, len(bc.chain)):
        assert bc.chain[i].previous_hash == bc.chain[i -
                                                     1].hash, f"Bloc {i} ne référence pas correctement le bloc précédent"

    print("✅ Test réussi : blocs correctement chaînés.")


def test_proof_of_work():
    print("\n\n🧪 === TEST PoW : minage avec difficulté variable=== 🧪")

    difficulty_easy = 2
    difficulty_hard = 5

    block_easy = Block("Test PoW Easy", "0", timestamp=1234)
    start_easy = time.time()
    block_easy.mine_block(difficulty_easy)
    end_easy = time.time()
    duration_easy = end_easy - start_easy

    block_hard = Block("Test PoW Hard", "0", timestamp=1234)
    start_hard = time.time()
    block_hard.mine_block(difficulty_hard)
    end_hard = time.time()
    duration_hard = end_hard - start_hard

    print(f"Durée minage difficulté {difficulty_easy}: {duration_easy:.4f} s")
    print(f"Durée minage difficulté {difficulty_hard}: {duration_hard:.4f} s")

    assert block_easy.hash.startswith(
        "0" * difficulty_easy), "❌ PoW échoué difficulté facile"
    assert block_hard.hash.startswith(
        "0" * difficulty_hard), "❌ PoW échoué difficulté difficile"
    assert duration_hard > duration_easy, "❌ Minage difficile devrait prendre plus de temps"

    print("\n ✅ Preuve de travail validée, impact du coût observé.")


def test_compute_merkle_root():
    print("\n\n🧪 === TEST : Calcul correct de la racine Merkle === 🧪\n")
    # Simuler 4 blocs avec des hash arbitraires
    blocks_hashes = [
        hashlib.sha256(f"Block {i}".encode()).hexdigest()
        for i in range(4)
    ]

    # Construire l'arbre de Merkle
    mt = MerkleTree(blocks_hashes)

    # Affichage de l'arbre
    mt.print_tree()

    # Calcul manuel attendu pour validation
    level1 = []
    for i in range(0, len(blocks_hashes), 2):
        combined = blocks_hashes[i] + blocks_hashes[i+1]
        level1.append(hashlib.sha256(combined.encode()).hexdigest())

    combined_root = level1[0] + level1[1]
    expected_root = hashlib.sha256(combined_root.encode()).hexdigest()

    assert mt.compute_merkle_root() == expected_root, "❌ Erreur : racine Merkle incorrecte !"
    print("✅ Test Merkle Tree réussi ! Racine :", mt.compute_merkle_root())


def compare_blockchains_table(bc1, bc2):
    print(f"\n{'Bloc':^6} | {'Hash BC1':^64} | {'Hash BC2':^64} | {'Égalité':^8}")
    print("-" * (6 + 3 + 64 + 3 + 64 + 3 + 8))
    for i in range(len(bc1.chain)):
        hash1 = bc1.chain[i].hash
        hash2 = bc2.chain[i].hash
        equal = "✅" if hash1 == hash2 else "❌"
        print(f"{i:^6} | {hash1:^64} | {hash2:^64} | {equal:^8}")

    # Affiche aussi la racine Merkle
    hashes1 = [block.hash for block in bc1.chain]
    hashes2 = [block.hash for block in bc2.chain]
    mt1 = MerkleTree(hashes1)
    mt2 = MerkleTree(hashes2)
    root1 = mt1.compute_merkle_root()
    root2 = mt2.compute_merkle_root()

    print(f"\nRacine Merkle BC1 : {root1}")
    print(f"Racine Merkle BC2 : {root2}")
    if root1 == root2:
        print("\n ✅ Les chaînes ont la même racine Merkle.")
    else:
        print("❌ Les chaînes ont des racines Merkle différentes.")


def test_blockchains_5_levels(num_blocks=16):
    difficulty = 3
    timestamps = [1000 + i for i in range(1, num_blocks + 1)]

    print(f"\n\n🧪 === TEST : CHAÎNES IDENTIQUES AVEC {num_blocks} BLOCS === 🧪 \n")
    bc1 = Blockchain(difficulty, genesis_timestamp=1000)
    bc2 = Blockchain(difficulty, genesis_timestamp=1000)

    for i in range(num_blocks):
        data = f"Transaction {i}"
        ts = timestamps[i]
        bc1.add_block(data, ts)
        bc2.add_block(data, ts)

    compare_blockchains_table(bc1, bc2)

    print(f"\n=== TEST : CORRUPTION DU BLOC 1 DANS bc2 AVEC {num_blocks} BLOCS ===")
    bc1 = Blockchain(difficulty, genesis_timestamp=1000)
    bc2 = Blockchain(difficulty, genesis_timestamp=1000)

    for i in range(num_blocks):
        data = f"Transaction {i}"
        ts = timestamps[i]
        bc1.add_block(data, ts)
        bc2.add_block(data, ts)

    # Corruption du bloc 1 dans bc2
    corrupted_block = bc2.chain[1]
    corrupted_block.update_data("Transaction modifiée")
    corrupted_block.mine_block(difficulty)

    # Reminer les blocs suivants pour maintenir la cohérence
    for i in range(2, len(bc2.chain)):
        bc2.chain[i].previous_hash = bc2.chain[i - 1].hash
        bc2.chain[i].nonce = 0
        bc2.chain[i].hash = bc2.chain[i].calculate_hash()
        bc2.chain[i].mine_block(difficulty)

    compare_blockchains_table(bc1, bc2)


def test_simulate_and_display_blockchains():
    print("\n\n🧪 === TEST : Simulation de 5 blockchains identiques === 🧪 \n")

    blockchains = simulate_decentralized_blockchains(num_instances=5)

    merkle_roots = []

    # Affiche les racines Merkle de chaque instance
    for idx, bc in enumerate(blockchains):
        hashes = [block.hash for block in bc.chain]
        mt = MerkleTree(hashes)
        root = mt.compute_merkle_root()
        merkle_roots.append(root)
        print(f"Instance {idx + 1} - Merkle Root : {root}")

    # Assert : toutes les racines doivent être identiques (même blockchain)
    first_root = merkle_roots[0]
    assert all(
        root == first_root for root in merkle_roots), "❌ Erreur : Les blockchains ne sont pas identiques !"
    print("\n ✅ Toutes les blockchains ont la même racine Merkle.")


def test_simulation_51_percent_attack():
    print("\n\n🧪 === TEST : Simulation d'une attaque à 51% === 🧪")

    difficulty = 3
    genesis_timestamp = 1000

    # Initialise 5 blockchains identiques
    blockchains = [Blockchain(difficulty, genesis_timestamp) for _ in range(5)]

    # Ajoute les mêmes blocs initiaux à toutes les blockchains
    for i in range(4):
        data = f"Transaction {i}"
        ts = genesis_timestamp + i + 1
        for bc in blockchains:
            bc.add_block(data, timestamp=ts)

    # Corruption d'une seule instance (minorité)
    blockchains[0].add_block("Corruption mineure", timestamp=2000)

    # Calcul Merkle Roots après corruption mineure
    roots_minor = []
    for bc in blockchains:
        hashes = [block.hash for block in bc.chain]
        mt = MerkleTree(hashes)
        roots_minor.append(mt.compute_merkle_root())

    print("\n--- Après corruption d'1 seule instance (minorité) ---")
    for i, root in enumerate(roots_minor):
        print(f"Instance {i+1} Merkle Root : {root}")

    majority_root_before = max(set(roots_minor), key=roots_minor.count)
    count_majority_before = roots_minor.count(majority_root_before)
    assert count_majority_before == 4, "Erreur : la minorité a pris le dessus après une seule corruption"
    print(f"\n✅ La minorité corrompue n'a PAS écrasé la majorité saine.")

    # Corruption de la majorité (3/5)
    # On crée un bloc corrompu sur la blockchain 0
    last_hash = blockchains[0].chain[-1].hash
    corrupted_block = Block("Corruption majeure", last_hash, timestamp=3000)
    corrupted_block.mine_block(difficulty)
    blockchains[0].chain.append(corrupted_block)

    # On remplace la chaîne des blockchains 1 et 2 par la chaîne corrompue de la blockchain 0 (copie)
    for i in [1, 2]:
        blockchains[i].chain = list(blockchains[0].chain)

    # Calcul Merkle Roots après corruption majeure
    roots_major = []
    for bc in blockchains:
        hashes = [block.hash for block in bc.chain]
        mt = MerkleTree(hashes)
        roots_major.append(mt.compute_merkle_root())

    print("\n--- Après corruption de la majorité (attaque 51%) ---")
    for i, root in enumerate(roots_major):
        print(f"Instance {i+1} Merkle Root : {root}")

    majority_root_after = max(set(roots_major), key=roots_major.count)
    count_majority_after = roots_major.count(majority_root_after)
    assert count_majority_after >= 3, "Erreur : la majorité corrompue n'a pas pris le dessus"

    print(f"\n❌ La majorité corrompue a PRIS le dessus (attaque 51%).")
    print(f"\najorité des racines : {majority_root_after}")


def test_detection_corruption_integrity():
    print("\n\n🧪 === TEST : Détection de corruption (intégrité distribuée) === 🧪")

    difficulty = 3
    genesis_timestamp = 1000
    num_instances = 5

    # Création des blockchains identiques
    blockchains = [Blockchain(difficulty, genesis_timestamp)
                   for _ in range(num_instances)]

    # Ajout des mêmes blocs initiaux
    for i in range(4):
        data = f"Transaction {i}"
        ts = genesis_timestamp + i + 1
        for bc in blockchains:
            bc.add_block(data, timestamp=ts)

    # Corruption d'une seule instance (ex: modifier un bloc dans la blockchain 0)
    print("\n-- Corruption de l'instance 1 --")
    corrupted_block = blockchains[0].chain[2]  # modifions le 3e bloc
    corrupted_block.data = "Corruption malveillante"
    corrupted_block.hash = corrupted_block.calculate_hash()  # recalcul hash (corrompu)

    # Vérification individuelle de chaque blockchain (validité hash & previous_hash)
    print("\n-- Validation individuelle des blockchains --")
    for i, bc in enumerate(blockchains):
        valid, bad_index = bc.is_chain_valid()
        status = "VALIDE" if valid else f"CORROMPUE au bloc {bad_index + 1}"
        print(f"Instance {i+1} : {status}")

    # Calcul des racines Merkle pour toutes les blockchains
    roots = []
    for bc in blockchains:
        hashes = [block.hash for block in bc.chain]
        mt = MerkleTree(hashes)
        roots.append(mt.compute_merkle_root())

    # Vérification de la majorité des racines Merkle (intégrité globale)
    majority_root = max(set(roots), key=roots.count)
    majority_count = roots.count(majority_root)

    print("\n-- Vérification de la racine Merkle majoritaire --")
    for i, root in enumerate(roots):
        match = "OK" if root == majority_root else "Différente"
        print(f"Instance {i+1} Merkle Root : {root} -> {match}")

    # Rejet automatique des blockchains corrompues
    print("\n-- Rejet automatique des blockchains corrompues --")
    for i, (bc, root) in enumerate(zip(blockchains, roots)):
        valid, _ = bc.is_chain_valid()
        if not valid or root != majority_root:
            print(f"Instance {i+1} rejetée pour corruption.")
        else:
            print(f"Instance {i+1} acceptée.")

    # Assertion : la majorité (non corrompue) doit être >= 4 (dans 5 instances)
    assert majority_count >= 4, "Erreur : la majorité saine devrait dominer"
    print("\n✅ La corruption d'une seule instance est détectée et rejetée.")


if __name__ == "__main__":

    test_creation_blockchain()

    test_proof_of_work()

    test_compute_merkle_root()

    test_simulate_and_display_blockchains()

    test_simulation_51_percent_attack()

    test_detection_corruption_integrity()

    test_blockchains_5_levels()
