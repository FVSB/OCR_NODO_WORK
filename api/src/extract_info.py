import requests


def get_country_editorial_by_doi(doi) -> str:
    # Paso 1: Obtener metadata del artículo
    url_work = f"https://api.crossref.org/works/{doi}"
    resp = requests.get(url_work)
    if resp.status_code != 200:
        return "DOI no encontrado"
    data = resp.json()

    # Paso 2: Extraer member_id
    member_url = data["message"].get("member")
    if not member_url:
        return "No se encontró el member_id"
    member_id = member_url.split("/")[-1]

    # Paso 3: Consultar la API de miembros
    url_member = f"https://api.crossref.org/members/{member_id}"
    resp_member = requests.get(url_member)
    if resp_member.status_code != 200:
        return "No se encontró información del miembro"
    data_member = resp_member.json()

    # Paso 4: Extraer país
    country_code = data_member["message"].get("location", "País no disponible")
    publisher = data_member["message"].get("primary-name", "Editorial desconocida")

    # return f"Editorial: {publisher}, País (código ISO): {country_code}"
    return country_code


def get_from_crossref(doi: str) -> dict:
    """
    Get Data from crossref

    Args:
        doi (str): _description_

    Returns:
        dict: _description_
    """
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    data = response.json()
    return data["message"]


def get_editorial_name_by_issn(issn: str):
    url = f"https://api.crossref.org/journals/{issn}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["message"].get("publisher", "Editorial no encontrada")
    else:
        return f"Error en la consulta: {response.status_code}"


class ExtractInfo:
    def __init__(
        self,
        table_name: str,
        url_server: str,
        user_name_next_cloud_api: str,
        password_next_cloud_api: str,
    ):
        self.table_name: str = table_name
        self.url_server: str = url_server
        self.user_name_next_cloud_api: str = user_name_next_cloud_api
        self.password_next_cloud_api: str = password_next_cloud_api

    def get_from_next_cloud(self, sub_url: str) -> dict:
        url = f"{self.url_server}/{sub_url}"
        headers = {"OCS-APIRequest": "true"}
        response = requests.post(
            url,
            auth=(self.user_name_next_cloud_api, self.password_next_cloud_api),
            headers=headers,
        )
        return response.json()

    def get_table_id(self):
        tables = self.get_from_next_cloud("index.php/apps/tables/api/1/tables")
        for table in tables:
            name = table["title"]
            if name == self.table_name:
                return table["id"]

        raise Exception(f"Don't exist table with title {name}")






############################
#                          #
#      OCR ZONE            #
#                          #
############################
    def get_title(self, data: dict):
        return {"columnId": 145, "value": data["title"][0]}  # Nombre publicacion

    def _get_authors(self, data: dict, is_internal: bool):

        authors = data["author"]
        lis = []
        if is_internal:
            lis = [
                author
                for author in authors
                if any(
                    aff["name"] == "Universidad de La Habana"
                    for aff in author["affiliation"]
                )
            ]
        else:
            lis = [
                author
                for author in authors
                if not any(
                    aff["name"] == "Universidad de La Habana"
                    for aff in author["affiliation"]
                )
            ]

        temp: str = ""
        for external in lis:
            temp += f"{external["family"] } {external["given"][0]}, "
        return temp

    def get_external_authors(self, data: dict) -> str:
        external_authors = self._get_authors(data, False)
        return ({"columnId": 150, "value": external_authors},)

    def get_internal_authors(self, data: dict) -> dict:
        internal_authors = self._get_authors(data, True)
        return ({"columnId": 175, "value": internal_authors},)

    def get_editorials(self, data):
        issn = data["ISSN"][0]
        editorial = get_editorial_name_by_issn(issn)
        return ({"columnId": 151, "value": editorial},)  # Revista

    def get_issns(self, data) -> dict:
        issns_type = data["issn-type"]
        issns_print = None
        issns_electronic = None
        for item in issns_type:
            value = item["value"]
            item_type = item["type"]
            if item_type == "electronic":
                issns_electronic = value
            elif item_type == "print":
                issns_print = value
        return ({"columnId": 153, "value": f"{issns_electronic}, {issns_print}"},)

    def get_country_publish(self, doi) -> dict:
        return {"columnId": 154, "value": get_country_editorial_by_doi(doi)}

    def get_url(self, url) -> dict:
        temp = f'{"{"}{"\""}title{"\""}:{"\""}{url}{"\""},{"\""}subline{"\""}:{"\""}URL{"\""},{"\""}providerId{"\""}:url,{"\""}value{"\""}:{"\""}{url}{"\""}'
        return {
            "columnId": 155,
            "value": temp,
        }

    def get_science_network(self) -> dict:
        return {"columnId": 535, "value": "Modelación Biomatemática"}

    def get_founders(self, data: dict) -> dict:
        founders = data["funder"]
        temp = ""
        for founder in founders:
            temp += f"{founder["name"]}, {founder["award"]}, \n"

        return (
            {
                "columnId": 536,
                "value": temp,
            },
        )

    def get_year(self, data):
        return {"columnId": 148, "value": data["indexed"]["date-parts"][0][0]}

    def get_publish_type(self, data) -> dict:
        return {"columnId": 146, "value": 0}

    def get_publish_group(self, data) -> dict:
        return {"columnId": 147, "value": 0}

    def get_serial_type(self, data) -> dict:
        return {"columnId": 152, "value": [0]}

    def get_is_international(self, data) -> dict:
        return {"columnId": 156, "value": 1}

    def get_origin_external_authors(self, data: dict) -> dict:
        return {"columnId": 157, "value": 0}

    def get_is_external_principal_author(self, data: dict) -> dict:
        authors = data["author"]
        principal_authors = [
            author for author in authors if author["sequence"] == "first"
        ]
        external_authors = [
            author
            for author in authors
            if not any(
                aff["name"] == "Universidad de La Habana"
                for aff in author["affiliation"]
            )
        ]
        val = 0
        if not principal_authors[0] in external_authors:
            val = 1
        return {"columnId": 158, "value": val}

    def get_means_of_dissemination(self, data: dict) -> dict:
        return {"columnId": 159, "value": 0}

    def get_quartile(self, data: str) -> dict:
        return {"columnId": 534, "value": 0}

    def get_report_area(self, data: dict) -> dict:
        return {
            "columnId": 160,
            "value": [{"id": "MATCOM", "type": 1, "displayName": "MATCOM"}],
        }

    def get_new_row(self, doi: str):

        data = get_from_crossref(doi)

        name = self.get_title(data)
        external_authors = self.get_external_authors(data)
        editorial = self.get_editorials(data)
        issns = self.get_issns(data)
        country_editorial = self.get_country_publish(doi)
        url_document: dict = self.get_url(doi)
        internal_authors = self.get_internal_authors(data)
        scient_network = self.get_science_network()
        funders = self.get_founders(data)
        year = self.get_year(data)
        publish_type = self.get_publish_type(data)
        publish_group = self.get_publish_group(data)
        serial_type = self.get_serial_type(data)
        is_international = self.get_is_international(data)
        origin_external_authors = self.get_origin_external_authors(data)
        is_external_principal_author = self.get_is_external_principal_author(data)
        means_of_dissemination = self.get_means_of_dissemination()
        quartile = self.get_quartile(data)
        report_area = self.get_report_area(data)

        table_colums = [
            name,
            external_authors,
            editorial,
            issns,
            country_editorial,
            url_document,
            internal_authors,
            scient_network,
            funders,
            year,
            publish_type,
            publish_group,
            serial_type,
            is_international,
            origin_external_authors,
            is_external_principal_author,
            means_of_dissemination,
            quartile,
            report_area,
        ]
        return table_colums

    def upload_data(self, doi):
        # https://minube.uh.cu/index.php/apps/tables/api/1/tables/24/rows

        url = f"{self.url_server}/index.php/apps/tables/api/1/tables/{self.get_table_id()}/rows"
        auth = (self.user_name_next_cloud_api, self.password_next_cloud_api)
        datos = self.get_new_row(doi)

        data_dict = {str(item["columnId"]): item["value"] for item in datos}

        payload = {"data": data_dict}

        headers = {"OCS-APIRequest": "true", "Content-Type": "application/json"}

        response = requests.post(url, json=payload, auth=auth, headers=headers)
        print(response.status_code)
        print(response.json())
