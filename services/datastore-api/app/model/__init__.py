from dataclasses import dataclass, field
from typing import List

@dataclass
class DatasetVariantData:
    filename: str = field(default=None)
    dataset_name: str = field(default=None)
    variant_name: str = field(default=None)
    content_type: str = field(default=None)
    size: int = field(default=None)


@dataclass
class DatasetVariant:
    name: str = field(default=None)
    dataset_name: str = field(default=None)
    data: List[DatasetVariantData] = field(default_factory=lambda : [])


@dataclass
class Dataset:
    name: str = field(default=None)
    variants: List[DatasetVariant] = field(default_factory=lambda : [])