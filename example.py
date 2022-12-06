from generator import ContractBindingGenerator


if __name__ == '__main__':
    paths = ['contracts/Example.sol', 'contracts/ManyTypes.sol']
    g = ContractBindingGenerator(paths)
    g.generate(output_dir='bindings')
