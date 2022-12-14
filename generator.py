import os
import re
from typing import List

from solcx import compile_files


class ContractBindingGenerator:
    def __init__(self, sources: List[str]):
        self.sources = sources
        self.template = """from typing import Optional, Union, Dict
from eth_typing import Address, ChecksumAddress
from web3 import Web3


class ContractAddressNotSet(Exception):
    pass
"""

    @staticmethod
    def sol_type_to_py_type(t):
        sol_type_to_py_type = {
            'uint256': 'int',
            'address': 'str',
            'bool': 'bool',
            'bytes1': 'bytes',
            'bytes': 'bytes',
            'bytes32': 'bytes',
            'int8': 'int',
            'tuple': 'tuple',
            'uint8': 'int'
        }

        return sol_type_to_py_type.get(t, None)

    @staticmethod
    def camel_to_snake(camel):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', camel).lower()

    @staticmethod
    def outputs_to_return_type(outputs):
        if len(outputs) == 1:
            o = outputs[0]
            return ContractBindingGenerator.sol_type_to_py_type(o.get('type', None))

        return None

    @staticmethod
    def inputs_to_argument_string(inputs):
        args = ['self']
        pass_into_method = []
        for i, ip in enumerate(inputs):
            t = ContractBindingGenerator.sol_type_to_py_type(ip.get('type', None))
            n = ip.get('name', None)
            if not n:
                n = f'a{i}'
            args.append(f"{ContractBindingGenerator.camel_to_snake(n)}: {t}")
            pass_into_method.append(ContractBindingGenerator.camel_to_snake(n))

        return ", ".join(pass_into_method), ", ".join(args)

    def generate(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output = compile_files(self.sources, output_values=["abi", "bin-runtime", "bin"])
        for key, val in output.items():
            contract_name = key.split(':')[1]
            file_name = f"{re.sub(r'(?<!^)(?=[A-Z])', '_', contract_name).lower()}.py"
            path = os.path.join(output_dir, file_name)
            abi = val.get('abi')
            has_constructor = 'constructor' in [elem.get('type') for elem in abi]
            byte_code = val.get('bin')
            code = self.template

            code += f"""
\nclass {contract_name}:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = {abi}
        self.bytecode = '{byte_code}'
        self.w3 = web3
            """

            if not has_constructor:
                code += """
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        """

            for elem in abi:
                ty = elem.get('type')
                inputs = elem.get('inputs', [])
                pass_into_method, statement_args = ContractBindingGenerator.inputs_to_argument_string(inputs)

                if ty == 'constructor':
                    code += f"""
    def deploy({statement_args}):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor({pass_into_method}).transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        """
                elif ty == 'function':
                    func_name = elem.get('name')
                    outputs = elem.get('outputs', [])
                    return_type = ContractBindingGenerator.outputs_to_return_type(outputs)
                    return_type_string = ' -> Dict'
                    return_stmt = f"return c.functions.{func_name}({pass_into_method}).buildTransaction()"
                    if return_type:
                        return_type_string = f' -> {return_type}'
                        return_stmt = f"return c.functions.{func_name}({pass_into_method}).call()"

                    code += f"""\n    def {ContractBindingGenerator.camel_to_snake(func_name)}({statement_args}){return_type_string}:"""
                    code += """\n        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    """
                    code += f"""\n        {return_stmt}\n"""

            with open(path, 'w+') as file:
                file.write(code)
