from __future__ import annotations

import json
from typing import Dict, List

from pydantic import BaseModel


class Parameters(BaseModel):
    apartments_json_path: str = "data/apartments.json"
    tenants_json_path: str = "data/tenants.json"
    transfers_json_path: str = "data/transfers.json"
    bills_json_path: str = "data/bills.json"


class Room(BaseModel):
    name: str
    area_m2: float


class Apartment(BaseModel):
    key: str
    name: str
    location: str
    area_m2: float
    rooms: Dict[str, Room]

    @staticmethod
    def from_json_file(file_path: str) -> Dict[str, Apartment]:
        with open(file_path, "r") as file:
            data = json.load(file)
        assert isinstance(data, dict), "Expected a dictionary of apartments"
        return {key: Apartment(**apartment) for key, apartment in data.items()}


class Tenant(BaseModel):
    name: str
    apartment: str
    room: str
    rent_pln: float
    deposit_pln: float
    date_agreement_from: str
    date_agreement_to: str

    @staticmethod
    def from_json_file(file_path: str) -> Dict[str, Tenant]:
        with open(file_path, "r") as file:
            data = json.load(file)
        assert isinstance(data, dict), "Expected a dictionary of tenants"
        return {key: Tenant(**tenant) for key, tenant in data.items()}


class Transfer(BaseModel):
    amount_pln: float
    date: str
    settlement_year: int | None
    settlement_month: int | None
    tenant: str

    @staticmethod
    def from_json_file(file_path: str) -> List[Transfer]:
        with open(file_path, "r") as file:
            data = json.load(file)
        assert isinstance(data, list), "Expected a list of transfers"
        return [Transfer(**transfer) for transfer in data]


class Bill(BaseModel):
    amount_pln: float
    date_due: str
    apartment: str
    settlement_year: int
    settlement_month: int
    type: str

    @staticmethod
    def from_json_file(file_path: str) -> List[Bill]:
        with open(file_path, "r") as file:
            data = json.load(file)
        assert isinstance(data, list), "Expected a list of bills"
        return [Bill(**bill) for bill in data]


class ApartmentSettlement(BaseModel):
    """Rozliczenie mieszkania za dany miesiąc/rok."""

    apart: str                      # identyfikator (klucz) mieszkania
    year: int                       # rok rozliczenia
    month: int                      # miesiąc rozliczenia
    total_bills_pln: float          # suma rachunków za media
    total_rents_pln: float          # suma czynszów
    remaining_amount_pln: float     # saldo (kwota pozostała do uregulowania)


class TenantSettlement(BaseModel):
    """Rozliczenie konkretnego najemcy za dany miesiąc/rok."""

    tenant: str                     # nazwa najemcy
    settlement_year: int
    settlement_month: int
    apartment: str                  # klucz mieszkania
    rent_pln: float                 # kwota czynszu do zapłaty
    bills_pln: float                # suma rachunków do zapłaty
    transfers_sum_pln: float        # suma przelewów przypisanych do rozliczenia
    balance_pln: float              # saldo: przelewy minus koszty

    @property
    def total_due_pln(self) -> float:
        """Łączna kwota do zapłaty (czynsz + rachunki)."""
        return self.rent_pln + self.bills_pln


class Manager:
    def __init__(self, parameters: Parameters) -> None:
        self.parameters = parameters
        self.apartments: Dict[str, Apartment] = {}
        self.tenants: Dict[str, Tenant] = {}
        self.transfers: List[Transfer] = []
        self.bills: List[Bill] = []
        self.load_data()

    def load_data(self) -> None:
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)


if __name__ == "__main__":
    parameters = Parameters()
    manager = Manager(parameters)

    for apartment in manager.apartments.values():
        print(apartment.key, apartment.name, apartment.location, apartment.area_m2)
        for room in apartment.rooms.values():
            print("  ", room.name, room.area_m2)

        for bill in manager.bills:
            if bill.apartment == apartment.key:
                print(
                    "  ",
                    bill.amount_pln,
                    bill.date_due,
                    bill.settlement_year,
                    bill.settlement_month,
                    bill.type,
                )

    for tenant in manager.tenants.values():
        print(
            tenant.name,
            tenant.apartment,
            tenant.room,
            tenant.rent_pln,
            tenant.deposit_pln,
            tenant.date_agreement_from,
            tenant.date_agreement_to,
        )
        for transfer in manager.transfers:
            if transfer.tenant == tenant.name:
                print(
                    "  ",
                    transfer.amount_pln,
                    transfer.date,
                    transfer.settlement_year,
                    transfer.settlement_month,
                )