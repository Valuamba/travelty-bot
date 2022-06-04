db.createUser(
{
    user: "valuamba",
    pwd: "16zomole",
    roles: [
        {
            role: "readWrite",
            db: "travelty"
        }
    ],
    mechanisms:[
    "SCRAM-SHA-1"
    ]
}
)

db.createUser({ user: "valuamba", pwd: "16zomole$$", roles: ["readWrite"]})