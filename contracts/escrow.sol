pragma ^0.5.0;

import "openzeppelin-solidity/contracts/math/SafeMath.sol";


contract RewardEscrow {
    using Safemath for uint256;
    uint256 public custodyTime;
    address owner;
    mapping(address => mapping(address => uint256)) public escrowBalance;
    // tracks the balance of an address associated to its respective escrow address
    mapping(address => mapping(address => uint256)) public custodyExpiration;
    //tracks the time before the escrow contract will expire 


  

    

}



