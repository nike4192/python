from catalog import Catalog

catalog = Catalog()

print(f'kwargs keys is {catalog.column_names}')

profiles_data = [
    ('Lawacky', 'Maria', '89777777777', 'Екатеринбург', 'maria@mail.ru'),
    ('Lawacky', 'Bob', '89888888888', 'Екатеринбург', 'bob@mail.ru')
]

print('# 1 ADD PROFILE(S)')
for profile_data in profiles_data:
    catalog.push_profile(profile_data)  # only for tuple data
    # or
    # catalog.add_profile(**dict(zip(catalog.column_names, profile_data))) # only kwargs

print('# 2 GET PROFILE')
profile = catalog.get_profile(first_name='Lawacky', last_name='Bob')
profile.print()

print('# 3 UPDATE PROFILE')
print(profile['last_name'], end=' -> ')  # before update Bob
catalog.update_profile(profile, last_name='Kevin')  # or profile.update(last_name='Kevin')
print(profile['last_name'])  # after update Kevin

print('# 4 DELETE PROFILE')
profile.print()
catalog.delete_profile(profile)  # or profile.delete()

print('# 5 GET ALL PROFILES')
profiles = catalog.get_all_profiles(first_name='Lawacky', limit=5)
for p in profiles:
    p.print()

print('# 6 CLEAR ALL PROFILES')
catalog.clear_all()

profiles = catalog.get_all_profiles()
print(profiles)
