import firebase_admin
from firebase_admin import credentials


from firebase_admin import firestore
from datetime import datetime

cred = credentials.Certificate("./firebase.json")
firebase_admin.initialize_app(cred)

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
	
print(get_trasactions('dinhanh', 5, 2023))
