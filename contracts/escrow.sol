pragma ^0.5.0;

import "openzeppelin-solidity/contracts/math/SafeMath.sol";

using Safemath for uint;

contract RewardEscrow {
    address owner;

    mapping(address => uint256) private _deposits;
}



