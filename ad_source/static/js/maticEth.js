// import * as Web3ProviderEngine  from 'web3-provider-engine';
// import * as RpcSource  from 'web3-provider-engine/subproviders/rpc';
// import * as HookedWalletSubprovider from 'web3-provider-engine/subproviders/hooked-wallet';

// console.log(Web3ProviderEngine)


export const matic = new Matic({
  maticProvider:  'https://testnet2.matic.network/',
  parentProvider: 'https://ropsten.infura.io/v3/70645f042c3a409599c60f96f6dd9fbc',
  rootChainAddress: '0x60e2b19b9a87a3f37827f2c8c8306be718a5f9b4',
  withdrawManagerAddress: '0x4ef2b60cdd4611fa0bc815792acc14de4c158d22',
  depositManagerAddress:'0x4072fab2a132bf98207cbfcd2c341adb904a67e9',
  maticWethAddress: '0x74f2a31a044c87bd687f2dcd5f858940f9c28d0c',  
  syncerUrl: 'https://matic-syncer2.api.matic.network/api/v1',
  watcherUrl: 'https://ropsten-watcher2.api.matic.network/api/v1',
})

