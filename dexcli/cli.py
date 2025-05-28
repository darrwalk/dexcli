#!/usr/bin/env python3
"""
dexcli - DEX Command Line Interface
A command-line interface for trading on decentralized exchanges using ccxt.
"""

import ccxt
import click
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
from tabulate import tabulate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DEXCLIClient:
    """Main client for interacting with the exchange"""
    
    def __init__(self, exchange_name: str = 'hyperliquid'):
        self.exchange_name = exchange_name
        self.exchange = None
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Initialize the exchange connection"""
        try:
            # Get credentials from environment variables
            api_key = os.getenv('DEXCLI_API_KEY', '')
            api_secret = os.getenv('DEXCLI_API_SECRET', '')
            
            # Initialize the exchange
            exchange_class = getattr(ccxt, self.exchange_name)
            self.exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })
            
            # For Hyperliquid specific configurations
            if self.exchange_name == 'hyperliquid':
                self.exchange.options = {
                    'defaultType': 'swap',  # Use perpetual futures
                }
                
        except AttributeError:
            raise ValueError(f"Exchange '{self.exchange_name}' not supported by ccxt")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize exchange: {str(e)}")
    
    def create_order(self, symbol: str, side: str, order_type: str, amount: float, 
                    price: Optional[float] = None) -> Dict[str, Any]:
        """Create a new order"""
        try:
            if order_type == 'limit' and price is None:
                raise ValueError("Price is required for limit orders")
            
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )
            return order
        except Exception as e:
            raise RuntimeError(f"Failed to create order: {str(e)}")
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to cancel order: {str(e)}")
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get the status of a specific order"""
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            raise RuntimeError(f"Failed to fetch order status: {str(e)}")
    
    def list_orders(self, symbol: Optional[str] = None, status: str = 'open') -> List[Dict[str, Any]]:
        """List orders with optional filtering"""
        try:
            if status == 'open':
                orders = self.exchange.fetch_open_orders(symbol)
            elif status == 'closed':
                orders = self.exchange.fetch_closed_orders(symbol)
            else:
                orders = self.exchange.fetch_orders(symbol)
            return orders
        except Exception as e:
            raise RuntimeError(f"Failed to fetch orders: {str(e)}")
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        try:
            positions = self.exchange.fetch_positions()
            return positions
        except Exception as e:
            raise RuntimeError(f"Failed to fetch positions: {str(e)}")
    
    def close_position(self, symbol: str, reduce_only: bool = True) -> Dict[str, Any]:
        """Close a position by creating a counter order"""
        try:
            # Fetch current position
            positions = self.exchange.fetch_positions([symbol])
            if not positions:
                raise ValueError(f"No open position found for {symbol}")
            
            position = positions[0]
            contracts = abs(position['contracts'])
            side = 'sell' if position['side'] == 'long' else 'buy'
            
            # Create market order to close position
            order = self.exchange.create_order(
                symbol=symbol,
                type='market',
                side=side,
                amount=contracts,
                params={'reduceOnly': reduce_only}
            )
            return order
        except Exception as e:
            raise RuntimeError(f"Failed to close position: {str(e)}")
    
    def get_open_orders(self, symbol: str) -> List[Dict[str, Any]]:
        """Get open orders for a specific symbol"""
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            raise RuntimeError(f"Failed to fetch open orders: {str(e)}")
    
    def list_markets(self) -> List[Dict[str, Any]]:
        """List all available markets"""
        try:
            markets = self.exchange.fetch_markets()
            return markets
        except Exception as e:
            raise RuntimeError(f"Failed to fetch markets: {str(e)}")

# CLI Commands
@click.group()
@click.pass_context
def cli(ctx):
    """dexcli - DEX Command Line Interface"""
    ctx.ensure_object(dict)
    ctx.obj['client'] = DEXCLIClient()

@cli.command()
@click.option('--symbol', '-s', required=True, help='Trading symbol (e.g., BTC/USDT)')
@click.option('--side', '-d', type=click.Choice(['buy', 'sell']), required=True, help='Order side')
@click.option('--type', '-t', type=click.Choice(['market', 'limit']), default='limit', help='Order type')
@click.option('--amount', '-a', type=float, required=True, help='Order amount')
@click.option('--price', '-p', type=float, help='Order price (required for limit orders)')
@click.pass_context
def create(ctx, symbol, side, type, amount, price):
    """Create a new order"""
    client = ctx.obj['client']
    try:
        order = client.create_order(symbol, side, type, amount, price)
        click.echo(f"Order created successfully!")
        click.echo(f"Order ID: {order['id']}")
        click.echo(f"Status: {order['status']}")
        click.echo(json.dumps(order, indent=2))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--order-id', '-i', required=True, help='Order ID to cancel')
@click.option('--symbol', '-s', required=True, help='Trading symbol')
@click.pass_context
def cancel(ctx, order_id, symbol):
    """Cancel an existing order"""
    client = ctx.obj['client']
    try:
        result = client.cancel_order(order_id, symbol)
        click.echo(f"Order {order_id} cancelled successfully!")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--order-id', '-i', required=True, help='Order ID to check')
@click.option('--symbol', '-s', required=True, help='Trading symbol')
@click.pass_context
def status(ctx, order_id, symbol):
    """Get the status of a specific order"""
    client = ctx.obj['client']
    try:
        order = client.get_order_status(order_id, symbol)
        click.echo(f"Order Status: {order['status']}")
        click.echo(f"Type: {order['type']}")
        click.echo(f"Side: {order['side']}")
        click.echo(f"Amount: {order['amount']}")
        click.echo(f"Filled: {order['filled']}")
        if order.get('price'):
            click.echo(f"Price: {order['price']}")
        click.echo(f"Created: {datetime.fromtimestamp(order['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--symbol', '-s', help='Filter by trading symbol')
@click.option('--status', '-t', type=click.Choice(['open', 'closed', 'all']), default='open', help='Order status filter')
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def orders(ctx, symbol, status, format):
    """List orders"""
    client = ctx.obj['client']
    try:
        orders_list = client.list_orders(symbol, status)
        
        if not orders_list:
            click.echo("No orders found.")
            return
        
        if format == 'json':
            click.echo(json.dumps(orders_list, indent=2))
        else:
            # Format as table
            headers = ['ID', 'Symbol', 'Type', 'Side', 'Amount', 'Filled', 'Price', 'Status', 'Created']
            rows = []
            for order in orders_list:
                rows.append([
                    order['id'][:8] + '...',
                    order['symbol'],
                    order['type'],
                    order['side'],
                    f"{order['amount']:.4f}",
                    f"{order['filled']:.4f}",
                    f"{order.get('price', 'N/A')}",
                    order['status'],
                    datetime.fromtimestamp(order['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
                ])
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def positions(ctx, format):
    """Show open positions"""
    client = ctx.obj['client']
    try:
        positions_list = client.get_positions()
        
        # Filter only open positions
        open_positions = [p for p in positions_list if p['contracts'] != 0]
        
        if not open_positions:
            click.echo("No open positions found.")
            return
        
        if format == 'json':
            click.echo(json.dumps(open_positions, indent=2))
        else:
            # Format as table
            headers = ['Symbol', 'Side', 'Contracts', 'Avg Price', 'Mark Price', 'PnL', 'PnL %', 'Margin']
            rows = []
            for pos in open_positions:
                rows.append([
                    pos['symbol'],
                    pos['side'],
                    f"{pos['contracts']:.4f}",
                    f"{pos.get('averagePrice', 'N/A')}",
                    f"{pos.get('markPrice', 'N/A')}",
                    f"{pos.get('unrealizedPnl', 0):.2f}",
                    f"{pos.get('percentage', 0):.2f}%",
                    f"{pos.get('initialMargin', 0):.2f}"
                ])
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--symbol', '-s', required=True, help='Position symbol to close')
@click.option('--confirm', '-y', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def close(ctx, symbol, confirm):
    """Close an open position"""
    client = ctx.obj['client']
    try:
        # Get current position info
        positions = client.get_positions()
        position = next((p for p in positions if p['symbol'] == symbol and p['contracts'] != 0), None)
        
        if not position:
            click.echo(f"No open position found for {symbol}")
            return
        
        # Show position details
        click.echo(f"Position to close:")
        click.echo(f"Symbol: {position['symbol']}")
        click.echo(f"Side: {position['side']}")
        click.echo(f"Contracts: {position['contracts']}")
        click.echo(f"Unrealized PnL: {position.get('unrealizedPnl', 0):.2f}")
        
        if not confirm:
            if not click.confirm("Are you sure you want to close this position?"):
                click.echo("Cancelled.")
                return
        
        # Close the position
        order = client.close_position(symbol)
        click.echo(f"Position closed successfully!")
        click.echo(f"Order ID: {order['id']}")
        click.echo(f"Status: {order['status']}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--symbol', '-s', required=True, help='Trading symbol (e.g., BTC/USDT)')
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def get_open_orders(ctx, symbol, format):
    """Get open orders for a specific symbol"""
    client = ctx.obj['client']
    try:
        orders_list = client.get_open_orders(symbol)
        
        if not orders_list:
            click.echo(f"No open orders found for {symbol}")
            return
        
        if format == 'json':
            click.echo(json.dumps(orders_list, indent=2))
        else:
            # Format as table
            headers = ['ID', 'Type', 'Side', 'Amount', 'Filled', 'Price', 'Status', 'Created']
            rows = []
            for order in orders_list:
                rows.append([
                    order['id'][:12] + '...' if len(order['id']) > 12 else order['id'],
                    order['type'],
                    order['side'],
                    f"{order['amount']:.4f}",
                    f"{order['filled']:.4f}",
                    f"{order.get('price', 'N/A')}",
                    order['status'],
                    datetime.fromtimestamp(order['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
                ])
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
            click.echo(f"\nTotal open orders: {len(orders_list)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--active', '-a', is_flag=True, help='Show only active markets')
@click.option('--type', '-t', type=click.Choice(['spot', 'swap', 'future']), help='Filter by market type')
@click.option('--quote', '-q', help='Filter by quote currency (e.g., USDT)')
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.pass_context
def markets(ctx, active, type, quote, format):
    """List available markets"""
    client = ctx.obj['client']
    try:
        markets_list = client.list_markets()
        
        # Apply filters
        if active:
            markets_list = [m for m in markets_list if m.get('active', True)]
        if type:
            markets_list = [m for m in markets_list if m.get('type') == type]
        if quote:
            markets_list = [m for m in markets_list if m.get('quote') == quote]
        
        if not markets_list:
            click.echo("No markets found matching the criteria.")
            return
        
        if format == 'json':
            click.echo(json.dumps(markets_list, indent=2))
        else:
            # Format as table
            headers = ['Symbol', 'Type', 'Base', 'Quote', 'Active', 'Min Amount', 'Min Cost']
            rows = []
            for market in markets_list[:50]:  # Limit to 50 for readability
                rows.append([
                    market['symbol'],
                    market.get('type', 'N/A'),
                    market.get('base', 'N/A'),
                    market.get('quote', 'N/A'),
                    '✓' if market.get('active', True) else '✗',
                    f"{market.get('limits', {}).get('amount', {}).get('min', 'N/A')}",
                    f"{market.get('limits', {}).get('cost', {}).get('min', 'N/A')}"
                ])
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
            if len(markets_list) > 50:
                click.echo(f"\n... and {len(markets_list) - 50} more markets")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

# Additional utility commands
@cli.command()
@click.pass_context
def info(ctx):
    """Show exchange information"""
    client = ctx.obj['client']
    try:
        exchange = client.exchange
        click.echo(f"Exchange: {exchange.name}")
        click.echo(f"Version: {exchange.version}")
        click.echo(f"Rate Limit: {'Enabled' if exchange.enableRateLimit else 'Disabled'}")
        click.echo(f"Has CORS: {exchange.has.get('CORS', False)}")
        click.echo(f"Has Public API: {exchange.has.get('publicAPI', False)}")
        click.echo(f"Has Private API: {exchange.has.get('privateAPI', False)}")
        
        # Show available features
        click.echo("\nAvailable Features:")
        features = [
            ('Fetch Ticker', 'fetchTicker'),
            ('Fetch Tickers', 'fetchTickers'),
            ('Fetch Order Book', 'fetchOrderBook'),
            ('Fetch Trades', 'fetchTrades'),
            ('Fetch OHLCV', 'fetchOHLCV'),
            ('Create Order', 'createOrder'),
            ('Cancel Order', 'cancelOrder'),
            ('Fetch Orders', 'fetchOrders'),
            ('Fetch Open Orders', 'fetchOpenOrders'),
            ('Fetch Closed Orders', 'fetchClosedOrders'),
            ('Fetch Positions', 'fetchPositions'),
            ('Fetch Balance', 'fetchBalance'),
        ]
        
        for name, key in features:
            supported = exchange.has.get(key, False)
            status = '✓' if supported else '✗'
            click.echo(f"  {status} {name}")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
