# marketplace_handler

Package to interact with marketplaces.

## Installation

### pip
```bash
pip install marketplace_handler
```

### poetry
```bash
poetry add marketplace_handler
```

## Usage
### Wildberries
```python
from marketpalce_handler import Wildberries

marketplace = Wildberries(
    token_id=0,
    token_service_token="your_token",
    token_service_url="https://your_token_url",
    mapping_url="https://your_mapping_url",
)

marketplace.refresh_price("id", 0)
```        
### Ozon
```python
from marketpalce_handler import Ozon
ozon = Ozon(
    client_id="client_id",
    api_key="api_key",
    collector_api_key="collector_api_key",
    collector_url="https://collector_url",
)
```