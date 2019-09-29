pragma ^0.5.0;

import "openzeppelin-solidity/contracts/math/SafeMath.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v2.3.0/contracts/token/ERC20/ERC20.sol"


contract RewardEscrow {
    using Safemath for uint256;
    uint256 public custodyTime;
    address owner;
    mapping(address => mapping(address => uint256)) public escrowBalance;
    // tracks the balance of an address associated to its respective escrow address
    mapping(address => mapping(address => uint256)) public custodyExpiration;
    //tracks the time before the escrow contract will expire 


function deposit(IERC20Token token, uint256 amount) public {
    require(token.transferFrom(msg.sender, this, amount));
    escrowBalance[msg.sender][token].add(amount);
    //set escrow expiration
}



  

    

}



