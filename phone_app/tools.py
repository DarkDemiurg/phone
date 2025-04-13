def get_user_agent():    
    model = 'UNIV'
    build_time = '20250413'
    try:
        with open('os-release') as f:
            lines = f.readlines()
            model = 'UNIV'
            for line in lines:
                parts = line.split('=')
                if len(parts) == 2:
                    if parts[0] == 'MODEL':
                        model = parts[1].strip('"\n')
                    if parts[0] == 'BUILD_TIME':
                        build_time = parts[1].strip('"\n')      
    except Exception:
        pass

    return f'{model}/{build_time}'