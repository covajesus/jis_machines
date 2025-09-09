# Mejoras sugeridas para el método store en collection_class

# Opción 1: Usar merge() de SQLAlchemy para upsert automático
def store_improved_v1(self, collection_inputs):
    """
    Versión mejorada usando merge() para operaciones upsert automáticas
    """
    tz = pytz.timezone('America/Santiago')
    current_date = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    collection_inputs['added_date'] = collection_inputs['added_date'].split(" ")[0]

    credit_note_amount = DteClass(self.db).verifiy_credit_note_amount(
        collection_inputs['branch_office_id'], 
        collection_inputs['cashier_id'], 
        collection_inputs['added_date']
    )

    # Calcular montos
    if credit_note_amount > 0:
        cash_gross_total = int(collection_inputs['cash_gross_amount']) - int(credit_note_amount)
        cash_net_total = round(int(cash_gross_total)/1.19)
    else:
        cash_gross_total = int(collection_inputs['cash_gross_amount'])
        cash_net_total = round(int(cash_gross_total)/1.19)

    try:
        # Buscar registro existente
        existing = self.db.query(CollectionModel).filter(
            CollectionModel.branch_office_id == collection_inputs['branch_office_id'],
            CollectionModel.cashier_id == collection_inputs['cashier_id'],
            CollectionModel.added_date == collection_inputs['added_date']
        ).first()

        if existing:
            # Actualizar registro existente
            existing.cash_gross_amount = cash_gross_total
            existing.cash_net_amount = cash_net_total
            existing.card_gross_amount = collection_inputs['card_gross_amount']
            existing.card_net_amount = collection_inputs['card_net_amount']
            existing.total_tickets = collection_inputs['total_tickets']
            existing.updated_date = current_date
            action = "updated"
        else:
            # Crear nuevo registro
            collection = CollectionModel(
                branch_office_id=collection_inputs['branch_office_id'],
                cashier_id=collection_inputs['cashier_id'],
                cash_gross_amount=cash_gross_total,
                cash_net_amount=cash_net_total,
                card_gross_amount=collection_inputs['card_gross_amount'],
                card_net_amount=collection_inputs['card_net_amount'],
                total_tickets=collection_inputs['total_tickets'],
                added_date=collection_inputs['added_date'],
                updated_date=current_date
            )
            self.db.add(collection)
            action = "created"

        self.db.commit()
        return f"Collection {action} successfully"

    except Exception as e:
        self.db.rollback()
        error_message = str(e)
        return f"Error: {error_message}"


# Opción 2: Usar ON DUPLICATE KEY UPDATE (específico para MySQL)
def store_improved_v2(self, collection_inputs):
    """
    Versión usando SQL nativo con ON DUPLICATE KEY UPDATE (MySQL)
    """
    from sqlalchemy import text
    
    tz = pytz.timezone('America/Santiago')
    current_date = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    collection_inputs['added_date'] = collection_inputs['added_date'].split(" ")[0]

    # Calcular montos...
    cash_gross_total = int(collection_inputs['cash_gross_amount'])
    cash_net_total = round(int(cash_gross_total)/1.19)

    try:
        sql = text("""
            INSERT INTO collections 
            (branch_office_id, cashier_id, cash_gross_amount, cash_net_amount, 
             card_gross_amount, card_net_amount, total_tickets, added_date, updated_date)
            VALUES 
            (:branch_office_id, :cashier_id, :cash_gross_amount, :cash_net_amount,
             :card_gross_amount, :card_net_amount, :total_tickets, :added_date, :updated_date)
            ON DUPLICATE KEY UPDATE
                cash_gross_amount = VALUES(cash_gross_amount),
                cash_net_amount = VALUES(cash_net_amount),
                card_gross_amount = VALUES(card_gross_amount),
                card_net_amount = VALUES(card_net_amount),
                total_tickets = VALUES(total_tickets),
                updated_date = VALUES(updated_date)
        """)
        
        self.db.execute(sql, {
            'branch_office_id': collection_inputs['branch_office_id'],
            'cashier_id': collection_inputs['cashier_id'],
            'cash_gross_amount': cash_gross_total,
            'cash_net_amount': cash_net_total,
            'card_gross_amount': collection_inputs['card_gross_amount'],
            'card_net_amount': collection_inputs['card_net_amount'],
            'total_tickets': collection_inputs['total_tickets'],
            'added_date': collection_inputs['added_date'],
            'updated_date': current_date
        })
        
        self.db.commit()
        return "Collection processed successfully"
        
    except Exception as e:
        self.db.rollback()
        return f"Error: {str(e)}"
