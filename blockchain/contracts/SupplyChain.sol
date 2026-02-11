// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract S {
    struct I { uint i; string n; bool v; }
    mapping(uint => I) public m;
    function add(uint _i, string memory _n, bool _v) public {
        m[_i] = I(_i, _n, _v);
    }
}