import engine

def main():
    flt = engine.merge_raw()
    staff = engine.create_staff()
    df = engine.assign_agent(flt, staff)
    df = engine.create_kpi(df)
    engine.save_data(df)

if __name__ == "__main__":
    main()