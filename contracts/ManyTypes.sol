contract ManyTypes {
    // booleans
    bool public b;

    // unsigned ints
    uint8 public u8;
    uint256 public u256;
    uint256[] public u256s;

    // signed ints
    int8 public i8;

    // addresses
    address public addr;
    address[] public addrs;

    // bytes
    bytes1 public b1;

    // structs
    struct S {
      address sa;
      bytes32 sb;
    }
    mapping(address => S) addrStructs;

    function updateBool(bool x) public { b = x; }
    function updateUint8(uint8 x) public { u8 = x; }
    function updateUint256(uint256 x) public { u256 = x; }
    function updateUintArray(uint256[] memory x) public { u256s = x; }
    function updateInt8(int8 x) public { i8 = x; }
    function updateAddr(address x) public { addr = x; }
    function updateBytes1(bytes1 x) public { b1 = x; }
    function updateMapping(S memory x) public { addrStructs[x.sa] = x; }
}