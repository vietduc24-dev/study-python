app/
│
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   ├── auth.py
│   ├── dependency.py
│   └── exception.py
│
├── common/
│   ├── enums/
│   ├── utils/
│   ├── middleware/
│   ├── pagination/
│   └── response.py
│
├── modules/
│
│   ├── auth/
│   ├── users/
│   ├── workspace/
│   ├── projects/
│   ├── tasks/
│   ├── finance/
│   ├── budget/
│   ├── dashboard/
│   ├── reports/
│   ├── notifications/
│   └── settings/
│
└── main.py

ví dụ trong mỗi module 
tasks/

├── router.py
├── service.py
├── repository.py
├── model.py
├── schema.py
├── dependency.py
└── validator.py

integrations/

    gmail/

    bank/

    aws/

    firebase/