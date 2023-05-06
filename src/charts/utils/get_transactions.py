from firebase_admin import firestore

db = firestore.client()

def get_trasactions(user, month, year):
	transactions = db.collection(u'transaction')

	# get all transactions not filter
	transactions = transactions.stream()

	output = []
	for transaction in transactions:
		data = transaction.to_dict()

		if data['from'] != user:
			continue
		if data['status'] != 'confirmed':
			continue
		
		created_at = data['timestamp']
		if created_at.month != month or created_at.year != year:
			continue

		output.append(data)

	return output
