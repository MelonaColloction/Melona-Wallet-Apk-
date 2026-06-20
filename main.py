import json
import os
import secrets
import time
import random
import string
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserListView
from PIL import Image as PILImage

Window.size = (400, 700)

class MemeCoin:
    def __init__(self, name, symbol, decimals, total_supply, owner, contract_id, logo="🪙", logo_image="", max_buy_percent=0.01, max_sell_percent=0.5):
        self.name = name
        self.symbol = symbol
        self.decimals = decimals
        self.total_supply = total_supply
        self.owner = owner
        self.contract_id = contract_id
        self.logo = logo
        self.logo_image = logo_image
        self.balances = {}
        self.history = []
        self.max_buy_percent = max_buy_percent
        self.max_sell_percent = max_sell_percent
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self._init_owner()
    
    def _init_owner(self):
        self.balances[self.owner] = self.total_supply
        self.history.append(f"✅ {self.symbol} created by {self.owner[:10]}... with {self.total_supply:,.0f} tokens")
    
    def get_balance(self, addr):
        return self.balances.get(addr, 0)
    
    def is_owner(self, addr):
        return addr == self.owner
    
    def buy(self, addr, amount):
        if amount <= 0:
            return False, "Amount must be positive"
        
        if self.is_owner(addr):
            circulation = sum(self.balances.values())
            if circulation + amount > self.total_supply:
                return False, f"Total supply exhausted. Only {self.total_supply - circulation:,.0f} left"
            self.balances[addr] = self.get_balance(addr) + amount
            self.history.append(f"OWNER BUY {amount:,.0f} {self.symbol} by {addr[:10]}...")
            return True, self.get_balance(addr)
        
        max_buy = self.total_supply * self.max_buy_percent
        if amount > max_buy:
            return False, f"Max buy per wallet is {max_buy:,.0f} {self.symbol}"
        
        circulation = sum(self.balances.values())
        if circulation + amount > self.total_supply:
            return False, f"Total supply exhausted. Only {self.total_supply - circulation:,.0f} left"
        
        self.balances[addr] = self.get_balance(addr) + amount
        self.history.append(f"BUY {amount:,.0f} {self.symbol} by {addr[:10]}...")
        return True, self.get_balance(addr)
    
    def sell(self, addr, amount):
        bal = self.get_balance(addr)
        if bal == 0:
            return False, "No balance"
        
        if amount <= 0:
            return False, "Amount must be positive"
        
        if amount > bal:
            return False, f"Insufficient balance. You have {bal:,.0f}"
        
        if self.is_owner(addr):
            self.balances[addr] = bal - amount
            self.history.append(f"OWNER SELL {amount:,.0f} {self.symbol} by {addr[:10]}...")
            return True, self.get_balance(addr)
        
        max_sell = bal * self.max_sell_percent
        if amount > max_sell:
            return False, f"Max sell per day is {max_sell:,.0f} {self.symbol} (50% of your balance)"
        
        self.balances[addr] = bal - amount
        self.history.append(f"SELL {amount:,.0f} {self.symbol} by {addr[:10]}...")
        return True, self.get_balance(addr)
    
    def transfer(self, from_addr, to_addr, amount):
        if from_addr not in self.balances:
            return False, "Sender not found"
        if to_addr not in self.balances:
            return False, "Recipient not found"
        if from_addr == to_addr:
            return False, "Cannot transfer to yourself"
        
        bal = self.get_balance(from_addr)
        if amount > bal:
            return False, f"Insufficient balance. You have {bal:,.0f}"
        
        self.balances[from_addr] = bal - amount
        self.balances[to_addr] = self.get_balance(to_addr) + amount
        self.history.append(f"TRANSFER {amount:,.0f} {self.symbol} from {from_addr[:10]}... to {to_addr[:10]}...")
        return True, self.get_balance(from_addr)
    
    def get_stats(self):
        circulation = sum(self.balances.values())
        return {
            "name": self.name,
            "symbol": self.symbol,
            "contract_id": self.contract_id,
            "decimals": self.decimals,
            "total_supply": self.total_supply,
            "circulation": circulation,
            "remaining": self.total_supply - circulation,
            "holders": len(self.balances),
            "transactions": len(self.history),
            "owner": self.owner,
            "logo": self.logo,
            "logo_image": self.logo_image,
            "created": self.created_at,
            "max_buy": self.total_supply * self.max_buy_percent,
            "max_sell_percent": f"{self.max_sell_percent * 100}%"
        }


class MelonaWallet:
    def __init__(self):
        self.db_file = "melona_data.json"
        self.main_token = None
        self.meme_coins = {}
        self.wallets = {}
        self.balances = {}
        self.allowed_creators = {}
        self.data = self._load()
        self.current_address = None
        self._init_main_token()
    
    def _load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                return self._default()
        return self._default()
    
    def _default(self):
        return {
            "wallets": {},
            "balances": {},
            "meme_coins": {},
            "history": [],
            "saved_keys": {},
            "allowed_creators": {},
            "watched_tokens": {}
        }
    
    def _save(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _init_main_token(self):
        main_owner = "MLEb4ed27e5103efdbdd5031053fba5cdfa7706bbaf"
        main_private = "d640a76ad5a2249a95155f0bebe368048d6a2d64e8cc2e20030b4c516d42ece5"
        logo = "🍉"
        logo_image = "melona_logo.png"
        
        if "main_token" not in self.data:
            self.data["main_token"] = {
                "name": "Melona",
                "symbol": "MLE",
                "decimals": 8,
                "total_supply": 5000000,
                "owner": main_owner,
                "logo": logo,
                "logo_image": logo_image,
                "balances": {},
                "history": [],
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self.data["main_token"]["balances"][main_owner] = 5000000
            self.data["wallets"][main_owner] = main_private
            self.data["saved_keys"][main_owner] = {
                "name": "OWNER",
                "private_key": main_private,
                "created": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save()
        
        self.main_token = MemeCoin(
            name=self.data["main_token"]["name"],
            symbol=self.data["main_token"]["symbol"],
            decimals=self.data["main_token"]["decimals"],
            total_supply=self.data["main_token"]["total_supply"],
            owner=self.data["main_token"]["owner"],
            contract_id="MLE",
            logo=self.data["main_token"].get("logo", "🍉"),
            logo_image=self.data["main_token"].get("logo_image", "melona_logo.png")
        )
        self.main_token.balances = self.data["main_token"]["balances"]
        self.main_token.history = self.data["main_token"]["history"]
        
        if "meme_coins" not in self.data:
            self.data["meme_coins"] = {}
        
        for coin_id, coin_data in self.data["meme_coins"].items():
            coin = MemeCoin(
                name=coin_data["name"],
                symbol=coin_data["symbol"],
                decimals=coin_data["decimals"],
                total_supply=coin_data["total_supply"],
                owner=coin_data["owner"],
                contract_id=coin_data.get("contract_id", coin_id),
                logo=coin_data.get("logo", "🪙"),
                logo_image=coin_data.get("logo_image", ""),
                max_buy_percent=coin_data.get("max_buy_percent", 0.01),
                max_sell_percent=coin_data.get("max_sell_percent", 0.5)
            )
            coin.balances = coin_data["balances"]
            coin.history = coin_data["history"]
            self.meme_coins[coin_id] = coin
        
        self.allowed_creators = self.data.get("allowed_creators", {})
        
        if "watched_tokens" not in self.data:
            self.data["watched_tokens"] = {}
        self._save()
    
    def _save_main_token(self):
        self.data["main_token"]["balances"] = self.main_token.balances
        self.data["main_token"]["history"] = self.main_token.history
        self.data["main_token"]["logo_image"] = self.main_token.logo_image
        self._save()
    
    def _save_meme_coin(self, coin_id):
        if "meme_coins" not in self.data:
            self.data["meme_coins"] = {}
        
        self.data["meme_coins"][coin_id] = {
            "name": self.meme_coins[coin_id].name,
            "symbol": self.meme_coins[coin_id].symbol,
            "decimals": self.meme_coins[coin_id].decimals,
            "total_supply": self.meme_coins[coin_id].total_supply,
            "owner": self.meme_coins[coin_id].owner,
            "contract_id": self.meme_coins[coin_id].contract_id,
            "logo": self.meme_coins[coin_id].logo,
            "logo_image": self.meme_coins[coin_id].logo_image,
            "balances": self.meme_coins[coin_id].balances,
            "history": self.meme_coins[coin_id].history,
            "created_at": self.meme_coins[coin_id].created_at,
            "max_buy_percent": self.meme_coins[coin_id].max_buy_percent,
            "max_sell_percent": self.meme_coins[coin_id].max_sell_percent
        }
        self._save()
    
    def create_wallet(self, name=None):
        addr = "MLE" + secrets.token_hex(20)
        priv = secrets.token_hex(32)
        self.data["wallets"][addr] = priv
        self.data["balances"][addr] = "0.0"
        if not name:
            name = addr[:8]
        self.data["saved_keys"][addr] = {
            "name": name,
            "private_key": priv,
            "created": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        if addr not in self.data["watched_tokens"]:
            self.data["watched_tokens"][addr] = []
        self._save()
        return addr, priv
    
    def recover_wallet(self, private_key):
        private_key = private_key.strip()
        for addr, priv in self.data["wallets"].items():
            if priv == private_key:
                return addr
        return None
    
    def get_balance(self, addr, token_type="main", coin_id=None):
        if token_type == "main":
            return self.main_token.get_balance(addr)
        elif token_type == "meme" and coin_id in self.meme_coins:
            return self.meme_coins[coin_id].get_balance(addr)
        return 0
    
    def buy_token(self, addr, token_type="main", coin_id=None, amount=None):
        if token_type == "main":
            if amount is None:
                amount = 0.01
            result = self.main_token.buy(addr, amount)
            if result[0]:
                self._save_main_token()
            return result
        elif token_type == "meme" and coin_id in self.meme_coins:
            result = self.meme_coins[coin_id].buy(addr, amount)
            if result[0]:
                self._save_meme_coin(coin_id)
            return result
        return False, "Token not found"
    
    def sell_token(self, addr, token_type="main", coin_id=None, amount=None):
        if token_type == "main":
            if amount is None:
                amount = self.main_token.get_balance(addr) * 0.5
            result = self.main_token.sell(addr, amount)
            if result[0]:
                self._save_main_token()
            return result
        elif token_type == "meme" and coin_id in self.meme_coins:
            if amount is None:
                amount = self.meme_coins[coin_id].get_balance(addr) * 0.5
            result = self.meme_coins[coin_id].sell(addr, amount)
            if result[0]:
                self._save_meme_coin(coin_id)
            return result
        return False, "Token not found"
    
    def transfer_token(self, from_addr, to_addr, amount, token_type="main", coin_id=None):
        if token_type == "main":
            result = self.main_token.transfer(from_addr, to_addr, amount)
            if result[0]:
                self._save_main_token()
            return result
        elif token_type == "meme" and coin_id in self.meme_coins:
            result = self.meme_coins[coin_id].transfer(from_addr, to_addr, amount)
            if result[0]:
                self._save_meme_coin(coin_id)
            return result
        return False, "Token not found"
    
    def is_owner(self, addr):
        return addr == self.main_token.owner
    
    def is_allowed_creator(self, addr):
        return addr in self.allowed_creators
    
    def allow_creator(self, owner_addr, creator_addr):
        if not self.is_owner(owner_addr):
            return False, "Only owner can allow creators"
        if creator_addr not in self.data["wallets"]:
            return False, "Creator address not found"
        self.allowed_creators[creator_addr] = {
            "allowed_by": owner_addr,
            "allowed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "used": False
        }
        self.data["allowed_creators"] = self.allowed_creators
        self._save()
        return True, f"✅ {creator_addr[:16]}... can now create one meme coin"
    
    def can_create_meme(self, addr):
        if self.is_owner(addr):
            return True, "owner"
        if addr in self.allowed_creators and not self.allowed_creators[addr].get("used", False):
            return True, "allowed"
        return False, None
    
    def use_creator_permission(self, addr):
        if addr in self.allowed_creators:
            self.allowed_creators[addr]["used"] = True
            self.data["allowed_creators"] = self.allowed_creators
            self._save()
    
    def generate_contract_id(self, symbol):
        rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{symbol}-{rand_part}"
    
    def create_meme_coin(self, name, symbol, decimals, total_supply, logo="🪙", logo_image=""):
        addr = self.current_address
        if not addr:
            return False, "No wallet loaded. Create or recover wallet first."
        
        can_create, role = self.can_create_meme(addr)
        if not can_create:
            return False, "❌ You don't have permission to create meme coins. Only owner or allowed creators can."
        
        contract_id = self.generate_contract_id(symbol.upper())
        while any(coin.contract_id == contract_id for coin in self.meme_coins.values()):
            contract_id = self.generate_contract_id(symbol.upper())
        
        if total_supply <= 0:
            return False, "Total supply must be greater than 0"
        
        if decimals < 0 or decimals > 18:
            return False, "Decimals must be between 0 and 18"
        
        coin = MemeCoin(name, symbol, decimals, total_supply, addr, contract_id, logo, logo_image)
        self.meme_coins[contract_id] = coin
        self._save_meme_coin(contract_id)
        
        if role == "allowed":
            self.use_creator_permission(addr)
        
        return True, f"✅ Meme coin {name} ({symbol}) created successfully!\n📜 Contract ID: {contract_id}"
    
    def add_watched_token(self, addr, contract_id):
        if contract_id not in self.meme_coins:
            return False, "Token not found"
        if addr not in self.data["watched_tokens"]:
            self.data["watched_tokens"][addr] = []
        if contract_id in self.data["watched_tokens"][addr]:
            return False, "Token already in your watch list"
        self.data["watched_tokens"][addr].append(contract_id)
        self._save()
        return True, f"✅ Token {self.meme_coins[contract_id].name} added to your watch list!"
    
    def get_watched_tokens(self, addr):
        return self.data["watched_tokens"].get(addr, [])
    
    def list_meme_coins(self, addr=None):
        if not self.meme_coins:
            return None
        coins = []
        watched = self.get_watched_tokens(addr) if addr else []
        for coin_id, coin in self.meme_coins.items():
            coins.append({
                "id": coin_id,
                "contract_id": coin.contract_id,
                "name": coin.name,
                "symbol": coin.symbol,
                "total_supply": coin.total_supply,
                "owner": coin.owner,
                "logo": coin.logo,
                "logo_image": coin.logo_image,
                "circulation": sum(coin.balances.values()),
                "holders": len(coin.balances),
                "watched": coin_id in watched
            })
        return coins
    
    def get_token_stats(self, token_type="main", coin_id=None):
        if token_type == "main":
            return self.main_token.get_stats()
        elif token_type == "meme" and coin_id in self.meme_coins:
            return self.meme_coins[coin_id].get_stats()
        return None
    
    def list_creators(self):
        return self.allowed_creators


class MainScreen(Screen):
    pass

class CreateWalletScreen(Screen):
    def create_wallet(self):
        app = App.get_running_app()
        wallet = app.wallet
        name = self.ids.wallet_name.text if self.ids.wallet_name.text else None
        addr, priv = wallet.create_wallet(name)
        wallet.current_address = addr
        self.ids.result_label.text = f"✅ Wallet created!\nAddress: {addr[:20]}...\n\n⚠️ SAVE YOUR PRIVATE KEY!"
        self.ids.full_address.text = f"Address: {addr}"
        self.ids.full_private.text = f"Private Key: {priv}"

class RecoverWalletScreen(Screen):
    def recover_wallet(self):
        app = App.get_running_app()
        wallet = app.wallet
        priv_key = self.ids.private_key.text.strip()
        if not priv_key:
            self.ids.result_label.text = "❌ Private key cannot be empty"
            return
        addr = wallet.recover_wallet(priv_key)
        if addr:
            wallet.current_address = addr
            self.ids.result_label.text = f"✅ Wallet recovered!\nAddress: {addr}\nBalance: {wallet.get_balance(addr, 'main'):.4f} MLE"
        else:
            self.ids.result_label.text = "❌ Invalid private key"

class MainMenuScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if addr:
            bal = wallet.get_balance(addr, "main")
            name = wallet.data["saved_keys"].get(addr, {}).get("name", "Unknown")
            self.ids.wallet_info.text = f"Active: {name} | Balance: {bal:.4f} MLE"
            if wallet.is_owner(addr):
                self.ids.wallet_info.text = f"👑 OWNER | Balance: {bal:,.4f} MLE"
        else:
            self.ids.wallet_info.text = "🔑 No wallet loaded"

class BuyMLEScreen(Screen):
    def buy_mle(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if not addr:
            self.ids.result_label.text = "❌ Create or recover wallet first"
            return
        
        amount = self.ids.amount.text.strip()
        if not amount:
            amount = "0.01"
        try:
            amount = float(amount)
        except:
            self.ids.result_label.text = "❌ Invalid amount"
            return
        
        ok, result = wallet.buy_token(addr, "main", None, amount)
        if ok:
            self.ids.result_label.text = f"✅ Buy successful!\nBalance: {result:.4f} MLE"
        else:
            self.ids.result_label.text = f"❌ {result}"

class SellMLEScreen(Screen):
    def sell_mle(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if not addr:
            self.ids.result_label.text = "❌ Create or recover wallet first"
            return
        
        bal = wallet.get_balance(addr, "main")
        self.ids.balance_label.text = f"Balance: {bal:.4f} MLE"
        
        amount = self.ids.amount.text.strip()
        if not amount:
            amount = str(bal * 0.5)
        try:
            amount = float(amount)
        except:
            self.ids.result_label.text = "❌ Invalid amount"
            return
        
        ok, result = wallet.sell_token(addr, "main", None, amount)
        if ok:
            self.ids.result_label.text = f"✅ Sell successful!\nBalance: {result:.4f} MLE"
        else:
            self.ids.result_label.text = f"❌ {result}"

class TransferMLEScreen(Screen):
    def transfer_mle(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if not addr:
            self.ids.result_label.text = "❌ Create or recover wallet first"
            return
        
        to_addr = self.ids.to_address.text.strip()
        if not to_addr:
            self.ids.result_label.text = "❌ Address cannot be empty"
            return
        
        amount = self.ids.amount.text.strip()
        if not amount:
            self.ids.result_label.text = "❌ Amount cannot be empty"
            return
        try:
            amount = float(amount)
        except:
            self.ids.result_label.text = "❌ Invalid amount"
            return
        
        ok, result = wallet.transfer_token(addr, to_addr, amount, "main")
        if ok:
            self.ids.result_label.text = f"✅ Transfer successful!\nNew balance: {result:.4f} MLE"
        else:
            self.ids.result_label.text = f"❌ {result}"

class CreateMemeCoinScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_image = ""
    
    def select_image(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        filechooser = FileChooserListView(
            path='/storage/emulated/0/Pictures',
            filters=['*.png', '*.jpg', '*.jpeg', '*.gif']
        )
        
        select_btn = Button(text="Select Image", size_hint_y=0.15)
        cancel_btn = Button(text="Cancel", size_hint_y=0.15)
        
        content.add_widget(filechooser)
        content.add_widget(select_btn)
        content.add_widget(cancel_btn)
        
        popup = Popup(title="Select Logo Image", content=content, size_hint=(0.9, 0.9))
        
        def on_select(instance):
            if filechooser.selection:
                path = filechooser.selection[0]
                filename = f"token_logo_{int(time.time())}.png"
                dest_path = os.path.join(os.getcwd(), filename)
                try:
                    img = PILImage.open(path)
                    img = img.resize((128, 128), PILImage.Resampling.LANCZOS)
                    img.save(dest_path, 'PNG')
                    self.selected_image = filename
                    self.ids.image_preview.source = dest_path
                    self.ids.image_preview.text = "✅ Image selected"
                    self.ids.image_preview.color = (0, 1, 0, 1)
                    popup.dismiss()
                except Exception as e:
                    self.ids.image_preview.text = f"❌ Error: {str(e)}"
                    popup.dismiss()
            else:
                self.ids.image_preview.text = "❌ No image selected"
                popup.dismiss()
        
        def on_cancel(instance):
            popup.dismiss()
        
        select_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=on_cancel)
        
        popup.open()
    
    def create_meme(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if not addr:
            self.ids.result_label.text = "❌ Create or recover wallet first"
            return
        
        can_create, role = wallet.can_create_meme(addr)
        if not can_create:
            self.ids.result_label.text = "❌ You don't have permission to create meme coins."
            return
        
        name = self.ids.coin_name.text.strip()
        symbol = self.ids.coin_symbol.text.strip().upper()
        decimals = self.ids.coin_decimals.text.strip()
        total_supply = self.ids.coin_supply.text.strip()
        logo_emoji = self.ids.coin_logo.text.strip() or "🪙"
        logo_image = self.selected_image
        
        if not name or not symbol:
            self.ids.result_label.text = "❌ Name and Symbol are required"
            return
        
        try:
            decimals = int(decimals) if decimals else 0
            if decimals < 0 or decimals > 18:
                self.ids.result_label.text = "❌ Decimals must be 0-18"
                return
        except:
            self.ids.result_label.text = "❌ Invalid decimals"
            return
        
        try:
            total_supply = float(total_supply) if total_supply else 1000000
            if total_supply <= 0:
                self.ids.result_label.text = "❌ Total supply must be > 0"
                return
        except:
            self.ids.result_label.text = "❌ Invalid total supply"
            return
        
        ok, result = wallet.create_meme_coin(name, symbol, decimals, total_supply, logo_emoji, logo_image)
        if ok:
            self.ids.result_label.text = result
            coin_id = result.split("📜 Contract ID: ")[-1].strip()
            self.ids.contract_id_label.text = f"Contract ID: {coin_id}"
            self.ids.contract_id_label.color = (0, 1, 0, 1)
        else:
            self.ids.result_label.text = f"❌ {result}"

class ListMemeCoinsScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        coins = wallet.list_meme_coins(addr)
        
        grid = self.ids.coins_grid
        grid.clear_widgets()
        
        if not coins:
            grid.add_widget(Label(text="No meme coins created yet", size_hint_y=None, height=50))
        else:
            for coin in coins:
                box = BoxLayout(size_hint_y=None, height=120, spacing=10, padding=10)
                box.size_hint_x = 1
                
                if coin['logo_image'] and os.path.exists(coin['logo_image']):
                    img = Image(source=coin['logo_image'], size_hint_x=0.2, allow_stretch=True, keep_ratio=True)
                else:
                    img = Label(text=coin['logo'], font_size='40sp', size_hint_x=0.2)
                
                info = BoxLayout(orientation='vertical', size_hint_x=0.8, spacing=2)
                watch_icon = "⭐ " if coin.get("watched") else ""
                info.add_widget(Label(
                    text=f"{watch_icon}{coin['name']} ({coin['symbol']})",
                    font_size='16sp',
                    bold=True,
                    size_hint_y=None,
                    height=30
                ))
                info.add_widget(Label(
                    text=f"Contract: {coin['contract_id']}",
                    font_size='12sp',
                    color=(0.5, 0.5, 0.5, 1),
                    size_hint_y=None,
                    height=25
                ))
                info.add_widget(Label(
                    text=f"Supply: {coin['total_supply']:,.0f} | Holders: {coin['holders']}",
                    font_size='12sp',
                    size_hint_y=None,
                    height=25
                ))
                
                box.add_widget(img)
                box.add_widget(info)
                grid.add_widget(box)

class BuyMemeCoinScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        coins = wallet.list_meme_coins(addr)
        if not coins:
            self.ids.coins_spinner.values = ["No coins"]
            self.ids.coins_spinner.text = "No coins"
        else:
            values = []
            for c in coins:
                values.append(f"{c['name']} ({c['symbol']})")
            self.ids.coins_spinner.values = values
            self.ids.coins_spinner.text = values[0]
        self.ids.result_label.text = ""
    
    def buy_meme(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if not addr:
            self.ids.result_label.text = "❌ Create or recover wallet first"
            return
        
        selected = self.ids.coins_spinner.text
        if selected == "No coins":
            self.ids.result_label.text = "❌ No coins available"
            return
        
        coins = wallet.list_meme_coins(addr)
        coin = None
        for c in coins:
            if f"{c['name']} ({c['symbol']})" == selected:
                coin = c
                break
        
        if not coin:
            self.ids.result_label.text = "❌ Coin not found"
            return
        
        amount = self.ids.amount.text.strip()
        try:
            amount = float(amount) if amount else 1
        except:
            self.ids.result_label.text = "❌ Invalid amount"
            return
        
        ok, result = wallet.buy_token(addr, "meme", coin['id'], amount)
        if ok:
            self.ids.result_label.text = f"✅ Buy successful!\nBalance: {result:,.0f} {coin['symbol']}"
        else:
            self.ids.result_label.text = f"❌ {result}"

class SellMemeCoinScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if not addr:
            self.ids.coins_spinner.values = ["No wallet"]
            self.ids.coins_spinner.text = "No wallet"
            return
        
        coins = wallet.list_meme_coins(addr)
        available = []
        for c in coins:
            bal = wallet.get_balance(addr, "meme", c['id'])
            if bal > 0:
                available.append(f"{c['name']} ({c['symbol']}) - {bal:,.0f}")
        
        if not available:
            self.ids.coins_spinner.values = ["No coins with balance"]
            self.ids.coins_spinner.text = "No coins with balance"
        else:
            self.ids.coins_spinner.values = available
            self.ids.coins_spinner.text = available[0]
        self.ids.result_label.text = ""
    
    def sell_meme(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if not addr:
            self.ids.result_label.text = "❌ Create or recover wallet first"
            return
        
        selected = self.ids.coins_spinner.text
        if selected in ["No wallet", "No coins with balance"]:
            self.ids.result_label.text = "❌ No coins to sell"
            return
        
        coins = wallet.list_meme_coins(addr)
        coin = None
        for c in coins:
            if c['name'] in selected:
                coin = c
                break
        
        if not coin:
            self.ids.result_label.text = "❌ Coin not found"
            return
        
        bal = wallet.get_balance(addr, "meme", coin['id'])
        if bal == 0:
            self.ids.result_label.text = "❌ You have no balance for this coin"
            return
        
        is_owner = wallet.is_owner(addr)
        max_sell = bal if is_owner else bal * 0.5
        
        amount = self.ids.amount.text.strip()
        if not amount:
            amount = str(max_sell)
        try:
            amount = float(amount)
        except:
            self.ids.result_label.text = "❌ Invalid amount"
            return
        
        if not is_owner and amount > max_sell:
            self.ids.result_label.text = f"❌ Max sell is {max_sell:,.0f} (50% of balance)"
            return
        
        ok, result = wallet.sell_token(addr, "meme", coin['id'], amount)
        if ok:
            self.ids.result_label.text = f"✅ Sell successful!\nNew balance: {result:,.0f} {coin['symbol']}"
        else:
            self.ids.result_label.text = f"❌ {result}"

class AddTokenScreen(Screen):
    def add_token(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if not addr:
            self.ids.result_label.text = "❌ Create or recover wallet first"
            return
        
        contract_id = self.ids.contract_id.text.strip().upper()
        if not contract_id:
            self.ids.result_label.text = "❌ Contract ID cannot be empty"
            return
        
        ok, result = wallet.add_watched_token(addr, contract_id)
        if ok:
            self.ids.result_label.text = result
            coin = wallet.meme_coins[contract_id]
            if coin.logo_image and os.path.exists(coin.logo_image):
                self.ids.token_image.source = coin.logo_image
                self.ids.token_image.text = ""
            else:
                self.ids.token_image.text = coin.logo
                self.ids.token_image.source = ""
            self.ids.token_info.text = f"Name: {coin.name}\nSymbol: {coin.symbol}\nSupply: {coin.total_supply:,.0f}\nHolders: {len(coin.balances)}"
        else:
            self.ids.result_label.text = f"❌ {result}"

class BalanceScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        wallet = app.wallet
        addr = wallet.current_address
        if not addr:
            self.ids.balance_text.text = "No wallet loaded"
            return
        
        bal = wallet.get_balance(addr, "main")
        text = f"MLE: {bal:.4f}\n\n"
        
        coins = wallet.list_meme_coins(addr)
        if coins:
            text += "Your Tokens (with balance):\n"
            has_balance = False
            for coin in coins:
                bal = wallet.get_balance(addr, "meme", coin['id'])
                if bal > 0:
                    logo = coin['logo']
                    if coin['logo_image'] and os.path.exists(coin['logo_image']):
                        logo = f"[img]{coin['logo_image']}[/img]"
                    text += f"   {logo} {coin['symbol']}: {bal:,.0f}\n"
                    has_balance = True
            if not has_balance:
                text += "   No tokens with balance\n"
            
            watched = wallet.get_watched_tokens(addr)
            if watched:
                text += "\nWatched Tokens:\n"
                for cid in watched:
                    if cid in wallet.meme_coins:
                        coin = wallet.meme_coins[cid]
                        bal = wallet.get_balance(addr, "meme", cid)
                        if bal == 0:
                            logo = coin['logo']
                            if coin['logo_image'] and os.path.exists(coin['logo_image']):
                                logo = f"[img]{coin['logo_image']}[/img]"
                            text += f"   {logo} {coin['symbol']} (0)\n"
        
        self.ids.balance_text.text = text

class StatsScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        wallet = app.wallet
        stats = wallet.main_token.get_stats()
        text = f"Main Token: {stats['name']} ({stats['symbol']})\n"
        text += f"Total Supply: {stats['total_supply']:,.0f}\n"
        text += f"Circulation: {stats['circulation']:,.0f}\n"
        text += f"Holders: {stats['holders']}\n"
        text += f"Transactions: {stats['transactions']}\n\n"
        
        coins = wallet.list_meme_coins()
        if coins:
            text += "Meme Coins:\n"
            for coin in coins:
                logo = coin['logo']
                if coin['logo_image'] and os.path.exists(coin['logo_image']):
                    logo = f"[img]{coin['logo_image']}[/img]"
                text += f"   {logo} {coin['name']} ({coin['symbol']})\n"
                text += f"      Contract: {coin['contract_id']}\n"
                text += f"      Supply: {coin['total_supply']:,.0f} | Holders: {coin['holders']}\n"
        
        self.ids.stats_text.text = text

class MelonaApp(App):
    def build(self):
        self.wallet = MelonaWallet()
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CreateWalletScreen(name='create_wallet'))
        sm.add_widget(RecoverWalletScreen(name='recover_wallet'))
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(BuyMLEScreen(name='buy_mle'))
        sm.add_widget(SellMLEScreen(name='sell_mle'))
        sm.add_widget(TransferMLEScreen(name='transfer_mle'))
        sm.add_widget(CreateMemeCoinScreen(name='create_meme'))
        sm.add_widget(ListMemeCoinsScreen(name='list_meme'))
        sm.add_widget(BuyMemeCoinScreen(name='buy_meme'))
        sm.add_widget(SellMemeCoinScreen(name='sell_meme'))
        sm.add_widget(AddTokenScreen(name='add_token'))
        sm.add_widget(BalanceScreen(name='balance'))
        sm.add_widget(StatsScreen(name='stats'))
        return sm

if __name__ == "__main__":
    MelonaApp().run()