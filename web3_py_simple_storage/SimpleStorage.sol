// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

// define a contract

contract SimpleStorage {

    // integer with size max 256 bits
    uint256 favoriteNumber;

    // struct
    // new ty pe of type People
    struct People {
        uint256 favoriteNumber;
        string name;
    }

    // new data structure of type mapping
    // maps the key( the name) to its associated value( favorite number)
    mapping(string => uint256) public nameToFavoriteNumber;

    // declare People type variable
    // People public person = People({favoriteNumber: 2, name: "Bob"});

    // declare a list of People. An array
    // empty dynamic array
    People[] public people;

    // create a function 
    // store user inputed _favoriteNumber in favoriteNumber
    function store(uint256 _favoriteNumber) public {
        favoriteNumber = _favoriteNumber;
    }

    // return function or retreive
    // non-state changing functions: view, pure(math operations)

    // pure functions just do some type of math operation
    // function add(uint256 num) public pure returns(uint256) {
    //     return num + num;
    // }

    // view functions read a state off the blockchain
    function retreive() public view returns(uint256) {
        return favoriteNumber;
    }

    // function to add a person to the People array and to the mapping
    function addPerson(string memory name, uint256 favNum) public {
        // create People object and push it onto people array
        people.push(People(favNum, name));

        // map the key(the name) to the favorite number
        nameToFavoriteNumber[name] = favNum;
    }

   
}