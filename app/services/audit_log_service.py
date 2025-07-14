from flask import request, jsonify, current_app
from datetime import datetime
from app.database import get_db_connection
from app.utils.validators import validate_integer, validate_string, validate_datetime

def insert_audit_log():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        current_app.logger.info(f"Received POST payload: {data}")

        # Required fields validation
        required_fields = {
            'ActionCode': (lambda x: validate_string(x, 'ActionCode', 50)),
            'Changes': (lambda x: validate_string(x, 'Changes', 1000000)),
            'ErrorCode': (lambda x: validate_string(x, 'ErrorCode', 50)),
            'Euser': (lambda x: validate_string(x, 'Euser', 25))
        }

        # Optional fields
        optional_fields = {
            'CaseID': (lambda x: validate_string(x, 'CaseID', 50, allow_empty=True)),
            'Operation': (lambda x: validate_string(x, 'Operation', 50, allow_empty=True)),
            'AssetCode': (lambda x: validate_string(x, 'AssetCode', 40, allow_empty=True)),
            'PlantCode': (lambda x: validate_string(x, 'PlantCode', 50, allow_empty=True))
        }

        # Validate required fields
        for field, validator in required_fields.items():
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
            is_valid, error = validator(data[field])
            if not is_valid:
                return jsonify({"error": error}), 400

        # Validate optional fields
        for field, validator in optional_fields.items():
            if field in data and data[field] is not None:
                is_valid, error = validator(data[field])
                if not is_valid:
                    return jsonify({"error": error}), 400

        # Prepare parameters
        params = {
            'ActionCode': str(data['ActionCode']),
            'Changes': str(data['Changes']),
            'ErrorCode': str(data['ErrorCode']),
            'Euser': str(data['Euser']),
            'CaseID': str(data.get('CaseID', '')),
            'Operation': str(data.get('Operation', '')),
            'AssetCode': str(data.get('AssetCode', '')),
            'PlantCode': str(data.get('PlantCode', ''))
        }

        conn = get_db_connection()
        cursor = conn.cursor()

        # Call USP_MES_InsertAuditLog stored procedure
        query = """
            EXEC USP_MES_InsertAuditLog 
            @ActionCode=%s, @Changes=%s, @ErrorCode=%s, @CaseID=%s, 
            @Operation=%s, @AssetCode=%s, @PlantCode=%s, @Euser=%s
        """
        cursor.execute(query, (
            params['ActionCode'], params['Changes'], params['ErrorCode'], params['CaseID'],
            params['Operation'], params['AssetCode'], params['PlantCode'], params['Euser']
        ))
        conn.commit()

        return jsonify({"message": "Audit log inserted successfully"}), 201

    except Exception as e:
        current_app.logger.error(f"Error in insert_audit_log: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_audit_logs():
    conn = None
    cursor = None
    try:
        # Extract query parameters
        params = {
            'SearchString': request.args.get('SearchString', ''),
            'FromDate': request.args.get('FromDate'),
            'ToDate': request.args.get('ToDate'),
            'PageNumber': request.args.get('PageNumber', '1'),
            'PageSize': request.args.get('PageSize', '50'),
            'ShowErrorOnly': request.args.get('ShowErrorOnly', ''),
            'CaseID': request.args.get('CaseID', ''),
            'Operation': request.args.get('Operation', ''),
            'ActionCode': request.args.get('ActionCode', ''),
            'Euser': request.args.get('Euser', ''),
            'PlantCode': request.args.get('PlantCode', '')
        }

        current_app.logger.info(f"Received GET params: {params}")

        # Type validations
        validations = {
            'SearchString': (lambda x: validate_string(x, 'SearchString', 500, allow_empty=True)),
            'FromDate': (lambda x: validate_datetime(x, 'FromDate') if x else (True, "")),
            'ToDate': (lambda x: validate_datetime(x, 'ToDate') if x else (True, "")),
            'PageNumber': (lambda x: validate_integer(x, 'PageNumber', min_value=1)),
            'PageSize': (lambda x: validate_integer(x, 'PageSize', min_value=1)),
            'ShowErrorOnly': (lambda x: validate_string(x, 'ShowErrorOnly', 1, allow_empty=True)),
            'CaseID': (lambda x: validate_string(x, 'CaseID', 50, allow_empty=True)),
            'Operation': (lambda x: validate_string(x, 'Operation', 50, allow_empty=True)),
            'ActionCode': (lambda x: validate_string(x, 'ActionCode', 50, allow_empty=True)),
            'Euser': (lambda x: validate_string(x, 'Euser', 50, allow_empty=True)),
            'PlantCode': (lambda x: validate_string(x, 'PlantCode', 50, allow_empty=True))
        }

        # Validate all parameters
        for field, validator in validations.items():
            is_valid, error = validator(params[field])
            if not is_valid:
                return jsonify({"error": error}), 400

        # Parse validated parameters
        search_string = params['SearchString']
        page_number = int(params['PageNumber'])
        page_size = int(params['PageSize'])
        show_error_only = params['ShowErrorOnly']
        case_id = params['CaseID']
        operation = params['Operation']
        action_code = params['ActionCode']
        euser = params['Euser']
        plant_code = params['PlantCode']

        # Handle date parameters
        try:
            from_date = datetime.strptime(params['FromDate'], '%Y-%m-%d %H:%M:%S') if params['FromDate'] else datetime(datetime.now().year, 1, 1)
            to_date = datetime.strptime(params['ToDate'], '%Y-%m-%d %H:%M:%S') if params['ToDate'] else datetime.now()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Call USP_MES_GetAuditLog stored procedure
        query = """
            EXEC USP_MES_GetAuditLog 
            @SearchString=%s, @FromDate=%s, @ToDate=%s, @PageNumber=%s, @PageSize=%s, 
            @ShowErrorOnly=%s, @CaseID=%s, @Operation=%s, @ActionCode=%s, @Euser=%s, @PlantCode=%s
        """
        cursor.execute(query, (
            search_string, from_date, to_date, page_number, page_size, 
            show_error_only, case_id, operation, action_code, euser, plant_code
        ))

        # Fetch results
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, datetime):
                    row_dict[columns[i]] = value.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    row_dict[columns[i]] = value
            results.append(row_dict)

        # Get total count if available
        total_count = len(results)
        if cursor.nextset():
            count_row = cursor.fetchone()
            total_count = count_row[0] if count_row else total_count

        return jsonify({
            "data": results,
            "total_count": total_count,
            "page_number": page_number,
            "page_size": page_size
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error in get_audit_logs: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()