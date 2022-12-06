// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract Example {
    uint public count;
    bytes32 someStuff;
    uint256 moreStuff;

    constructor(bytes32 stuff, uint256 extraStuff) payable  {
        someStuff = stuff;
        moreStuff = extraStuff;
    }

    // Function to get the current count
    function get() public view returns (uint) {
        return count;
    }

    // Function to increment count by 1
    function inc() public {
        count += 1;
    }

    // Function to decrement count by 1
    function dec() public {
        // This function will fail if count = 0
        count -= 1;
    }

    function incWith(uint val) public {
        count += val;
    }

    function incWithBytes(bytes memory byteArray) public {
        count += 1;
    }

    function paymeToIncrement(uint val) public payable {
        count += val;
    }

    function payExactToIncrement(uint val) public payable {
        require(msg.value == 10000000000000000, "must pay 0.01 Eth");
        count += val;
    }
}
