extraction_contract_invoice = {
    "invoice": {
        "memo": "",
        "due_date": "",
        "issue_date": "",
        "line_items": [
            {
                "item": {
                    "id": "",
                    "quantity": 0,
                    "item_name": "",
                    "unit_amount": 0
                },
                "class_name": "",
                "description": "",
                "total_amount": 0
            }
        ],
        "customer_id": "",
        "currency_code": "",
        "customer_name": "",
        "document_number": "",
        "additional_fields": {
            "addresses": [],
            "not_found": ""
        }
    }
}


extraction_contract_invoice_structure = {
    "invoice": {
        "required": True,
        "properties": {
            "memo": {
                "required": False,
                "displayName": "Memo"
            },
            "due_date": {
                "required": False,
                "displayName": "Due Date"
            },
            "issue_date": {
                "required": True,
                "displayName": "Issue Date"
            },
            "line_items": {
                "required": True,
                "properties": {
                    "item": {
                        "required": True,
                        "properties": {
                            "id": {
                                "required": False,
                                "displayName": "Item Id"
                            },
                            "quantity": {
                                "required": True,
                                "displayName": "Quantity"
                            },
                            "item_name": {
                                "required": True,
                                "displayName": "Item Name"
                            },
                            "unit_amount": {
                                "required": True,
                                "displayName": "Unit Amount"
                            }
                        },
                        "displayName": "Item Reference"
                    },
                    "class_id": {
                        "required": False,
                        "displayName": "Class Id"
                    },
                    "class_name": {
                        "required": False,
                        "displayName": "Class Name"
                    },
                    "description": {
                        "required": False,
                        "maxlength": 4000,
                        "displayName": "Description"
                    },
                    "total_amount": {
                        "required": True,
                        "displayName": "Total Amount"
                    },
                    "discount_amount": {
                        "required": False,
                        "displayName": "Discount Amount"
                    }
                },
                "displayName": "Line Items"
            },
            "customer_id": {
                "required": False,
                "displayName": "Customer Id"
            },
            "currency_code": {
                "required": True,
                "displayName": "Currency Code"
            },
            "customer_name": {
                "required": True,
                "displayName": "Customer Name"
            },
            "document_number": {
                "required": True,
                "maxlength": 11,
                "displayName": "Document Number"
            },
            "additional_fields": {
                "required": False,
                "properties": {
                    "addresses": {
                        "required": False,
                        "properties": {
                            "city": {
                                "required": False,
                                "displayName": "City"
                            },
                            "type": {
                                "required": False,
                                "displayName": "Type"
                            },
                            "region": {
                                "required": False,
                                "displayName": "Region"
                            },
                            "country": {
                                "required": False,
                                "displayName": "Country"
                            },
                            "address1": {
                                "required": False,
                                "displayName": "Address 1"
                            },
                            "address2": {
                                "required": False,
                                "displayName": "Address 2"
                            },
                            "postal_code": {
                                "required": False,
                                "displayName": "Postal Code"
                            }
                        },
                        "displayName": "Address"
                    }
                },
                "displayName": "Additional Field"
            }
        },
        "displayName": "Invoice"
    }
}


extraction_contract_bill = {
    "bill": {
        "vendor_id": "",
        "vendor_name": "",
        "due_date": "",
        "issue_date": "",
        "currency_code": "",
        "document_number": "",
        "memo": "",
        "line_items": [
            {
                "account_id": "",
                "account_name": "",
                "total_amount": 0,
                "description": "",
                "item": {
                    "id": "",
                    "item_name": "",
                    "quantity": 0,
                    "unit_amount": 0
                }
            }
        ],
    }
}

extraction_contract_bill_structure = {
    "bill": {
        "required": True,
        "properties": {
            "memo": {
                "required": False,
                "displayName": "Memo"
            },
            "due_date": {
                "required": False,
                "displayName": "Due Date"
            },
            "vendor_id": {
                "required": False,
                "displayName": "Vendor Id"
            },
            "issue_date": {
                "required": True,
                "displayName": "Issue Date"
            },
            "line_items": {
                "required": True,
                "properties": {
                    "item": {
                        "required": True,
                        "properties": {
                            "id": {
                                "required": False,
                                "displayName": "Id"
                            },
                            "quantity": {
                                "required": True,
                                "displayName": "Quantity"
                            },
                            "item_name": {
                                "required": True,
                                "displayName": "Item Name"
                            },
                            "unit_amount": {
                                "required": True,
                                "displayName": "Unit Amount"
                            }
                        },
                        "displayName": "Item"
                    },
                    "account_id": {
                        "required": False,
                        "displayName": "Account Id"
                    },
                    "description": {
                        "required": False,
                        "displayName": "Description"
                    },
                    "account_name": {
                        "required": True,
                        "displayName": "Account Name"
                    },
                    "total_amount": {
                        "required": True,
                        "displayName": "Total Amount"
                    }
                },
                "displayName": "Line Items"
            },
            "vendor_name": {
                "required": True,
                "displayName": "Vendor Name"
            },
            "currency_code": {
                "required": True,
                "displayName": "Currency Code"
            },
            "document_number": {
                "required": True,
                "displayName": "Document Number"
            }
        },
        "displayName": "Bill"
    }
}


extraction_contract_invoices_payments = {
    "invoice_payment": {
        "account_id": "",
        "account_name": "",
        "customer_id": "",
        "customer_name": "",
        "reference": "",
        "payment_method_id": "",
        "txn_date": "",
        "currency_code": "",
        "total_amount": 0,
        "memo": "",
        "linked_invoices": [
            {
                "id": "",
                "invoice_number": "",
                "allocated_at": "",
                "amount": 0
            }
        ],

    }
}


extraction_contract_invoice_payment_structure = {
    "invoice_payment": {
        "required": True,
        "properties": {
            "memo": {
                "required": False,
                "displayName": "Memo"
            },
            "txn_date": {
                "required": True,
                "displayName": "Transaction Date"
            },
            "reference": {
                "required": False,
                "displayName": "Reference Number"
            },
            "account_id": {
                "required": False,
                "displayName": "Account Id"
            },
            "customer_id": {
                "required": False,
                "displayName": "Customer Id"
            },
            "account_name": {
                "required": False,
                "displayName": "Account Name"
            },
            "total_amount": {
                "required": True,
                "displayName": "Total Amount"
            },
            "currency_code": {
                "required": True,
                "displayName": "Currency Code"
            },
            "customer_name": {
                "required": True,
                "displayName": "Customer Name"
            },
            "linked_invoices": {
                "required": False,
                "properties": {
                    "id": {
                        "required": False,
                        "displayName": "Id"
                    },
                    "amount": {
                        "required": False,
                        "displayName": "Amount"
                    },
                    "allocated_at": {
                        "required": False,
                        "displayName": "Allocated At"
                    },
                    "invoice_number": {
                        "required": False,
                        "displayName": "Invoice Number"
                    }
                },
                "displayName": "Linked Invoices"
            },
            "payment_method_id": {
                "required": False,
                "displayName": "Payment Method Id"
            }
        },
        "displayName": "Invoice Payment"
    }
}


extraction_contract_journal_entry = {
    "journal_entry": {
        "transaction_date": "",
        "currency_code": "",
        "memo": "",
        "line_items": [
            {
                "account_id": "",
                "account_name": "",
                "total_amount": "",
                "description": ""
            }
        ],

    }
}


extraction_contract_journal_entry_structure = {
    "journal_entry": {
        "required": True,
        "properties": {
            "memo": {
                "required": False,
                "displayName": "Memo"
            },
            "line_items": {
                "required": True,
                "properties": {
                    "account_id": {
                        "required": False,
                        "displayName": "Account Id"
                    },
                    "description": {
                        "required": False,
                        "maxlength": 4000,
                        "displayName": "Description"
                    },
                    "account_name": {
                        "required": True,
                        "displayName": "Account Name"
                    },
                    "total_amount": {
                        "required": True,
                        "displayName": "Total Amount"
                    }
                },
                "displayName": "Line Items"
            },
            "currency_code": {
                "required": True,
                "displayName": "Currency Code"
            },
            "transaction_date": {
                "required": True,
                "displayName": "Transaction Date"
            }
        },
        "displayName": "Journal Entry"
    }
}


extraction_contract_sales_order = {
    "SalesOrderAddRq": {
        "requestID": "",
        "SalesOrderAdd": {
            "CustomerRef": {
                "FullName": ""
            },
            "TemplateRef": {
                "FullName": ""
            },
            "TxnDate": "",
            "RefNumber": "",
            "BillAddress": {
                "Addr1": "",
                "Addr2": "",
                "City": "",
                "State": "",
                "PostalCode": ""
            },
            "ShipAddress": {
                "Addr1": "",
                "Addr2": "",
                "City": "",
                "State": "",
                "PostalCode": ""
            },
            "PONumber": "",
            "DueDate": "",
            "ShipDate": "",
            "Other": "",
            "SalesOrderLineAdd": [
                {
                    "ItemRef": {
                        "FullName": ""
                    },
                    "Desc": "",
                    "Quantity": "",
                    "Rate": ""
                },
                {
                    "ItemRef": {
                        "FullName": ""
                    },
                    "Desc": "",
                    "Quantity": "",
                    "Rate": ""
                }
            ]
        }
    }
}


extraction_contract_item_services = {
    "ItemServiceAddRq": {
        "requestID": "",
        "ItemServiceAdd": {
            "Name": "",
                    "IsActive": "",
                    "ClassRef": {
                        "FullName": ""
                    },
            "ParentRef": {
                        "FullName": ""
                    },
            "ManufacturerPartNumber": "",
            "UnitOfMeasureSetRef": {
                        "FullName": ""
                    },
            "IsTaxIncluded": "",
            "SalesTaxCodeRef": {
                        "FullName": ""
                    },
            "SalesOrPurchase": {
                        "Desc": "",
                        "Price": "",
                        "AccountRef": {
                            "FullName": ""
                        }
                    }
        }
    }
}


extraction_contract_customer = {
    "Customer": {
        "Name": "",
        "IsActive": "",
        "ClassRef": "",
        "ParentRef": "",
        "CompanyName": "",
        "Salutation": "",
        "FirstName": "",
        "MiddleName": "",
        "LastName": "",
        "JobTitle": "",
        "BillAddress": {
            "Addr1": "",
            "Addr2": "",
            "Addr3": "",
            "Addr4": "",
            "Addr5": "",
            "City": "",
            "State": "",
            "PostalCode": "",
            "Country": "",
            "Note": ""
        },
        "ShipAddress": {
            "Addr1": "",
            "Addr2": "",
            "Addr3": "",
            "Addr4": "",
            "Addr5": "",
            "City": "",
            "State": "",
            "PostalCode": "",
            "Country": "",
            "Note": ""
        },
        "Phone": "",
        "AltPhone": "",
        "Fax": "",
        "Email": "",
        "Cc": "",
        "Contact": "",
        "AltContact": "",
        "Contacts": {
            "Salutation": "",
            "FirstName": "",
            "MiddleName": "",
            "LastName": "",
            "JobTitle": ""
        },
        "CustomerTypeRef": "",
        "TermsRef": "",
        "SalesRepRef": "",
        "OpenBalance": "",
        "OpenBalanceDate": "",
        "SalesTaxCodeRef": "",
        "ItemSalesTaxRef": "",
        "AccountNumber": "",
        "JobStatus": "",
        "JobStartDate": "",
        "JobProjectedEndDate": "",
        "JobEndDate": "",
        "JobDesc": "",
        "JobTypeRef": "",
        "PreferredDeliveryMethod": ""
    }
}

extraction_contract_item_inventory = {

    "ItemInventoryAddRq": {
        "requestID": "",
        "ItemInventoryAdd": {
            "Name": "",
                    "IsActive": "",
                    "ClassRef": {
                        "FullName": ""
                    },
            "ParentRef": {
                        "FullName": ""
                    },
            "ManufacturerPartNumber": "",
            "UnitOfMeasureSetRef": {
                        "FullName": ""
                    },
            "IsTaxIncluded": "",
            "SalesTaxCodeRef": {
                        "FullName": ""
                    },
            "SalesDesc": "",
            "SalesPrice": "",
            "IncomeAccountRef": {
                        "FullName": ""
                    },
            "PurchaseDesc": "",
            "PurchaseCost": "",
            "PurchaseTaxCodeRef": {
                        "FullName": ""
                    },
            "COGSAccountRef": {
                        "FullName": ""
                    },
            "PrefVendorRef": {
                        "FullName": ""
                    },
            "AssetAccountRef": {
                        "FullName": ""
                    },
            "ReorderPoint": "",
            "Max": "",
            "QuantityOnHand": "",
            "TotalValue": "",
            "InventoryDate": ""
        }
    }
}
