pragma ^0.5.0;

import "openzeppelin-solidity/contracts/math/SafeMath.sol";


contract RewardEscrow {
    using Safemath for uint;

    address owner;

    mapping(address => uint256) private _deposits;
}



