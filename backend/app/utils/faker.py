from faker import Faker
import pandas as pd
import numpy as np
import random
from passlib.context import CryptContext
from datetime import datetime

Faker = Faker()
random.seed(42)
np.random.seed(42)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Using dummy users
users_df = pd.DataFrame({
    "user_id": range(1, 51),
    "name": [Faker.name() for _ in range(50)],
    "email": [Faker.unique.email() for _ in range(50)],
    "password": [pwd_context.hash("password123") for _ in range(50)]
})
users_df.to_csv("users.csv", index=False)

