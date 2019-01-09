
from core.ontology.stardog_query import get_query
from core.config_loading.ontology_xml_handler import OntologyXMLResultHandler



def pred_query(query,prefix):

    # 临时Ontology查询
    warning_sign_sparql = "SELECT ?hazard WHERE { :" + query + " :isWarningSignFor ?hazard }"
    ontology_res = get_query(warning_sign_sparql, "PREFIX : " + prefix)

    # 进行XML反解析

    dict = OntologyXMLResultHandler.xml_to_dict(ontology_res)

    return OntologyXMLResultHandler.get_uri_val(dict)


def metadata_query_hazards(hazards,prefix):

    query_value_str = ''
    for h in hazards:
        query_value_str = query_value_str+"(:" + h + ") "

    sql_script = "SELECT  ?hazard ?observation ?observedProperty ?dataSource ?metadata ?profile ?p ?value " +\
        "WHERE { ?observation :isObservationFor ?hazard . ?observedProperty :isObservedPropertyFor ?observation . " +\
        "?dataSource :isDataSourceFor ?observedProperty . ?dataSource :hasDataSourceMetadata ?metadata . ?metadata " +\
":hasProfile ?profile . ?profile ?p ?value . VALUES (?hazard) { " + query_value_str + " } . FILTER (?p != rdf:type) }"

    ontology_res = get_query(sql_script,"PREFIX : " + prefix)

    return ontology_res
