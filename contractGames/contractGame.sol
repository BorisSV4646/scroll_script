// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract Tictactoe {
    error Unauthorized();

    uint256 gameBoard = 0;
    uint256 internal constant HORIZONTAL_MASK = 0x3F;
    uint256 internal constant VERTICAL_MASK = 0x30C3;
    uint256 internal constant BR_TO_TL_DIAGONAL_MASK = 0x30303;
    uint256 internal constant BL_TO_TR_DIAGONAL_MASK = 0x3330;

    address internal playerOne;
    address internal playerTwo;
    address[] players;

    constructor(address _playerTwo) {
        require(_playerTwo != address(0));
        playerOne = msg.sender;
        playerTwo = _playerTwo;
        players.push(playerOne);
        players.push(playerTwo);
        gameBoard = gameBoard | (1 << 20);
    }

    modifier isPlayer(address _player) {
        if (_player != playerOne && _player != playerTwo) {
            revert Unauthorized();
        }
        _;
    }

    modifier isTurn(address _player) {
        require(
            ((gameBoard >> 18) & 0x1) == playerId(_player),
            "Not your turn"
        );
        _;
    }

    modifier moveIsValid(uint256 _move) {
        uint256 p1 = _move << 1;
        uint256 p2 = p1 + 1;
        uint256 _gameBoard = gameBoard;

        require(
            !(((_gameBoard >> p1) & 1) == 1 || ((_gameBoard >> p2) & 1) == 1),
            "invalid move"
        );
        require(_move < 9, "invalid move");
        _;
    }

    function playerId(address playerAddr) internal view returns (uint256) {
        return playerAddr == playerOne ? 0 : 1;
    }

    function newGame() external isPlayer(msg.sender) {
        gameBoard = 1 << 20;
    }

    function getGame() external view returns (uint256) {
        return gameBoard;
    }

    function move(
        uint256 _move
    )
        external
        isPlayer(msg.sender)
        isTurn(msg.sender)
        moveIsValid(_move)
        returns (uint256)
    {
        uint256 _gameBoard = gameBoard;

        require(
            (_gameBoard >> 19) & 1 == 0 && (_gameBoard >> 20) & 1 == 1,
            "Game has ended"
        );

        uint256 _playerId = playerId(msg.sender);

        _gameBoard = _gameBoard ^ (1 << ((_move << 1) + _playerId));

        gameBoard = _gameBoard ^ (1 << 18);

        uint256 gameState = checkState(_playerId);

        if (gameState == 1) {
            gameBoard = gameBoard ^ (1 << (19 + _playerId));
            return 1;
        } else if (gameState == 2) {
            return 2;
        }

        return 0;
    }

    function checkState(uint256 _playerId) public view returns (uint256) {
        uint256 _gameBoard = gameBoard;

        if (
            (_gameBoard & HORIZONTAL_MASK) ==
            ((HORIZONTAL_MASK / 3) << _playerId)
        ) {
            return 1;
        } else if (
            (_gameBoard & (HORIZONTAL_MASK << 6)) ==
            ((HORIZONTAL_MASK / 3) << _playerId) << 6
        ) {
            return 1;
        } else if (
            (_gameBoard & (HORIZONTAL_MASK << 12)) ==
            ((HORIZONTAL_MASK / 3) << _playerId) << 12
        ) {
            return 1;
        }

        if ((_gameBoard & VERTICAL_MASK) == (VERTICAL_MASK / 3) << _playerId) {
            return 1;
        } else if (
            (_gameBoard & (VERTICAL_MASK << 2)) ==
            ((VERTICAL_MASK / 3) << _playerId) << 2
        ) {
            return 1;
        } else if (
            (_gameBoard & (VERTICAL_MASK << 4)) ==
            ((VERTICAL_MASK / 3) << _playerId) << 4
        ) {
            return 1;
        }

        if (
            (_gameBoard & BR_TO_TL_DIAGONAL_MASK) ==
            (BR_TO_TL_DIAGONAL_MASK / 3) << _playerId
        ) {
            return 1;
        }

        if (
            (_gameBoard & BL_TO_TR_DIAGONAL_MASK) ==
            (BL_TO_TR_DIAGONAL_MASK / 3) << _playerId
        ) {
            return 1;
        }

        unchecked {
            for (uint256 x = 0; x < 9; x++) {
                if (_gameBoard & 1 == 0 && _gameBoard & 2 == 0) {
                    return 0;
                }
                _gameBoard = _gameBoard >> 2;
            }
            return 2;
        }
    }

    function getPlayers() public view returns (address[] memory) {
        return players;
    }
}
