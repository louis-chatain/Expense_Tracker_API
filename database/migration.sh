export FLASK_APP=../backend/app
echo "------going to migrate--------"
flask db migrate -m "updating table Celebrity to have a relation with table User"
echo "------going to upgrade--------"
flask db upgrade
echo "Database migration complete."