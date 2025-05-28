# dexcli - DEX Command Line Interface

A powerful command-line interface for cryptocurrency trading on decentralized exchanges using ccxt, initially supporting Hyperliquid.

## Features

- **Order Management**: Create, cancel, and monitor orders
- **Position Tracking**: View and close open positions
- **Market Data**: List available trading markets
- **Multiple Output Formats**: Table and JSON output options
- **Secure**: API credentials stored in environment variables

## Installation

### From Source

```bash
git clone https://github.com/darrwalk/dexcli.git
cd dexcli
pip install -e .
```

### Via pip (after publishing)

```bash
pip install dexcli
```

## Configuration

1. Create a `.env` file in your project directory:

```env
DEXCLI_API_KEY=your_hyperliquid_api_key
DEXCLI_API_SECRET=your_hyperliquid_api_secret
```

2. Or export environment variables:

```bash
export DEXCLI_API_KEY=your_hyperliquid_api_key
export DEXCLI_API_SECRET=your_hyperliquid_api_secret
```

## Usage

### Create Orders

```bash
# Create a limit buy order
dexcli create -s BTC/USDT -d buy -t limit -a 0.001 -p 50000

# Create a market sell order
dexcli create -s ETH/USDT -d sell -t market -a 0.1
```

### Manage Orders

```bash
# Get open orders for a symbol
dexcli get-open-orders -s BTC/USDT

# List all orders
dexcli orders

# Check order status
dexcli status -i <order_id> -s BTC/USDT

# Cancel an order
dexcli cancel -i <order_id> -s BTC/USDT
```

### Position Management

```bash
# Show all open positions
dexcli positions

# Close a position
dexcli close -s BTC/USDT

# Skip confirmation prompt
dexcli close -s BTC/USDT -y
```

### Market Information

```bash
# List all markets
dexcli markets

# Show only active USDT markets
dexcli markets -a -q USDT

# Output in JSON format
dexcli markets -f json
```

### Exchange Information

```bash
# Show exchange capabilities
dexcli info
```

## Command Reference

| Command | Description | Required Args |
|---------|-------------|---------------|
| `create` | Create a new order | symbol, side, amount |
| `cancel` | Cancel an existing order | order-id, symbol |
| `status` | Get order status | order-id, symbol |
| `orders` | List orders | - |
| `get-open-orders` | Get open orders for symbol | symbol |
| `positions` | Show open positions | - |
| `close` | Close a position | symbol |
| `markets` | List available markets | - |
| `info` | Show exchange information | - |

## Options

### Global Options
- `-f, --format [table|json]`: Output format (default: table)

### Create Order Options
- `-s, --symbol`: Trading symbol (e.g., BTC/USDT)
- `-d, --side [buy|sell]`: Order side
- `-t, --type [market|limit]`: Order type (default: limit)
- `-a, --amount`: Order amount
- `-p, --price`: Order price (required for limit orders)

### Market Filters
- `-a, --active`: Show only active markets
- `-t, --type [spot|swap|future]`: Filter by market type
- `-q, --quote`: Filter by quote currency

## Development

### Requirements

- Python 3.8+
- ccxt
- click
- tabulate
- python-dotenv

### Running Tests

```bash
python -m pytest tests/
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [ccxt](https://github.com/ccxt/ccxt) - A JavaScript / Python / PHP cryptocurrency trading API
- CLI powered by [Click](https://click.palletsprojects.com/)

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/darrwalk/dexcli/issues).
