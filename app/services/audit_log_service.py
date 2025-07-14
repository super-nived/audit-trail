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

        # Required fields with their type validations
        required_fields = {
            'ModuleID': (lambda x: validate_integer(x, 'ModuleID', min_value=1)),
            'AccessCode': (lambda x: validate_string(x, 'AccessCode', 40)),
            'ActionDesc': (lambda x: validate_string(x, 'ActionDesc', 100)),
            'Changes': (lambda x: validate_string(x, 'Changes', 1000000)),
            'ErrorCode': (lambda x: validate_string(x, 'ErrorCode', 50)),
            'PlantList': (lambda x: validate_string(x, 'PlantList', 100)),
            'Euser': (lambda x: validate_string(x, 'Euser', 25))
        }

        # Optional fields with their type validations
        optional_fields = {
            'CaseID': (lambda x: validate_string(x, 'CaseID', 50, allow_empty=True)),
            'Operation': (lambda x: validate_string(x, 'Operation', 50, allow_empty=True)),
            'AssetCode': (lambda x: validate_string(x, 'AssetCode', 40, allow_empty=True)),
            'Parameter1': (lambda x: validate_string(x, 'Parameter1', 50, allow_empty=True)),
            'Parameter2': (lambda x: validate_string(x, 'Parameter2', 50, allow_empty=True)),
            'Parameter3': (lambda x: validate_string(x, 'Parameter3', 50, allow_empty=True)),
            'Parameter4': (lambda x: validate_string(x, 'Parameter4', 50, allow_empty=True))
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
            'ModuleID': int(data['ModuleID']),
            'AccessCode': str(data['AccessCode']),
            'ActionDesc': str(data['ActionDesc']),
            'Changes': str(data['Changes']),
            'ErrorCode': str(data['ErrorCode']),
            'PlantList': str(data['PlantList']),
            'Euser': str(data['Euser']),
            'CaseID': str(data.get('CaseID', '')),
            'Operation': str(data.get('Operation', '')),
            'AssetCode': str(data.get('AssetCode', '')),
            'Parameter1': str(data.get('Parameter1', '')),
            'Parameter2': str(data.get('Parameter2', '')),
            'Parameter3': str(data.get('Parameter3', '')),
            'Parameter4': str(data.get('Parameter4', ''))
        }

        conn = get_db_connection()
        cursor = conn.cursor()

        # Call spInsertAuditLog stored procedure
        query = """
            EXEC spInsertAuditLog 
            @ModuleID=%s, @AccessCode=%s, @ActionDesc=%s, @Changes=%s, @ErrorCode=%s, @PlantList=%s, @Euser=%s, @CaseID=%s, @Operation=%s, @AssetCode=%s, @Parameter1=%s, @Parameter2=%s, @Parameter3=%s, @Parameter4=%s
        """
        cursor.execute(query, (
            params['ModuleID'], params['AccessCode'], params['ActionDesc'], params['Changes'],
            params['ErrorCode'], params['PlantList'], params['Euser'], params['CaseID'],
            params['Operation'], params['AssetCode'], params['Parameter1'],
            params['Parameter2'], params['Parameter3'], params['Parameter4']
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
            'ModuleID': request.args.get('ModuleID', '0'),
            'Text': request.args.get('Text', ''),
            'FromDate': request.args.get('FromDate'),
            'ToDate': request.args.get('ToDate'),
            'PageNumber': request.args.get('PageNumber', '1'),
            'PageSize': request.args.get('PageSize', '50'),
            'Euser': request.args.get('Euser', ''),
            'Err': request.args.get('Err', ''),
            'PlantList': request.args.get('PlantList', ''),
            'CaseID': request.args.get('CaseID', ''),
            'Operation': request.args.get('Operation', ''),
            'ActionDesc': request.args.get('ActionDesc', '')
        }

        current_app.logger.info(f"Received GET params: {params}")

        # Type validations
        validations = {
            'ModuleID': (lambda x: validate_integer(x, 'ModuleID', min_value=0)),
            'Text': (lambda x: validate_string(x, 'Text', 500, allow_empty=True)),
            'FromDate': (lambda x: validate_datetime(x, 'FromDate') if x else (True, "")),
            'ToDate': (lambda x: validate_datetime(x, 'ToDate') if x else (True, "")),
            'PageNumber': (lambda x: validate_integer(x, 'PageNumber', min_value=1)),
            'PageSize': (lambda x: validate_integer(x, 'PageSize', min_value=1)),
            'Euser': (lambda x: validate_string(x, 'Euser', 50, allow_empty=True)),
            'Err': (lambda x: validate_string(x, 'Err', 1, allow_empty=True)),
            'PlantList': (lambda x: validate_string(x, 'PlantList', 50, allow_empty=True)),
            'CaseID': (lambda x: validate_string(x, 'CaseID', 50, allow_empty=True)),
            'Operation': (lambda x: validate_string(x, 'Operation', 50, allow_empty=True)),
            'ActionDesc': (lambda x: validate_string(x, 'ActionDesc', 100, allow_empty=True))
        }

        # Validate all parameters
        for field, validator in validations.items():
            is_valid, error = validator(params[field])
            if not is_valid:
                return jsonify({"error": error}), 400

        # Parse validated parameters
        module_id = int(params['ModuleID'])
        text = params['Text']
        page_number = int(params['PageNumber'])
        page_size = int(params['PageSize'])
        euser = params['Euser']
        err = params['Err']
        plant_list = params['PlantList']
        case_id = params['CaseID']
        operation = params['Operation']
        action_desc = params['ActionDesc']

        # Handle date parameters
        try:
            from_date = datetime.strptime(params['FromDate'], '%Y-%m-%d %H:%M:%S') if params['FromDate'] else datetime(datetime.now().year, 1, 1)
            to_date = datetime.strptime(params['ToDate'], '%Y-%m-%d %H:%M:%S') if params['ToDate'] else datetime.now()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Call USPGet_Auditlog stored procedure
        query = """
            EXEC USPGet_Auditlog 
            @ModuleID=%s, @Text=%s, @FromDate=%s, @ToDate=%s, @PageNumber=%s, @PageSize=%s, @Euser=%s, @Err=%s, @PlantList=%s, @CaseID=%s, @Operation=%s, @ActionDesc=%s
        """
        cursor.execute(query, (
            module_id, text, from_date, to_date,
            page_number, page_size, euser, err,
            plant_list, case_id, operation, action_desc
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

        # Get total count
        total_count = 0
        if cursor.nextset():
            count_row = cursor.fetchone()
            total_count = count_row[0] if count_row else 0

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
