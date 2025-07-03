from fastapi import APIRouter, HTTPException
from .database import collection
from bson import ObjectId
from typing import List

from .models import Album, AlbumUpdateAno, AlbumUpdateGenero, UpdateCompositorNome

router = APIRouter()

@router.get("/artistas/contagem_discos", tags=["Queries do Trabalho"])
async def contar_discos_por_artista():
    pipeline = [
        {"$group": {"_id": "$artista", "totalDiscos": {"$sum": 1}}},
        {"$project": {"_id": 0, "artista": "$_id", "totalDiscos": 1}},
        {"$sort": {"totalDiscos": -1}}
    ]
    try:
        return list(collection.aggregate(pipeline))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/albuns/{id}/ano", tags=["Queries do Trabalho"])
async def corrigir_ano_lancamento(id: str, novo_ano: AlbumUpdateAno):
    try:
        operacao_update = {
            "$set": {
                "anoLancamento": novo_ano.anoLancamento
            }
        }
        
        resultado = collection.update_one(
            {"_id": ObjectId(id)}, 
            operacao_update
        )
        
        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Álbum com id {id} não encontrado.")
            
        if resultado.modified_count == 0:
            return {"message": "O ano de lançamento fornecido já era o valor atual. Nenhum dado foi alterado."}

        return {"message": f"Ano de lançamento do álbum {id} atualizado com sucesso."}

    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/albuns/remover-campo-catalogo", tags=["Queries do Trabalho"])
async def remover_campo_catalogo():
    try:
        operacao_update = {
            "$unset": { "numeroCatalogo": "" }
        }

        resultado = collection.update_many({}, operacao_update)

        return {
            "message": "Operação concluída com sucesso.",
            "documentos_modificados": resultado.modified_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/albuns/duracao", tags=["Queries do Trabalho"])
async def calcular_duracao_total_albuns():
    pipeline = [
        {
            "$unwind": "$faixas"
        },
        {
            "$group": {
                "_id": {
                    "id": "$_id",
                    "titulo": "$titulo"
                },
                "duracao_total_segundos": { "$sum": "$faixas.duracao_segundos" }
            }
        },
        {
            "$project": {
                "_id": "$_id.id",
                "titulo": "$_id.titulo",
                "duracao_em_segundos": "$duracao_total_segundos",
                "duracao_em_minutos": {
                    "$divide": ["$duracao_total_segundos", 60]
                }
            }
        },
        {
            "$sort": {
                "duracao_em_minutos": -1
            }
        }
    ]
    
    try:
        resultados = list(collection.aggregate(pipeline))
        
        for res in resultados:
            res["_id"] = str(res["_id"])

        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/albuns/{id}/genero", tags=["Queries do Trabalho"])
async def adicionar_genero_album(id: str, novo_genero: AlbumUpdateGenero):
    try:
        operacao_update = {
            "$addToSet": { "generos": novo_genero.genero }
        }

        resultado = collection.update_one(
            {"_id": ObjectId(id)},
            operacao_update
        )

        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Álbum com id {id} não encontrado.")
            
        if resultado.modified_count == 0:
            return {"message": f"O gênero '{novo_genero.genero}' já existe neste álbum. Nenhum dado foi alterado."}

        return {"message": f"Gênero '{novo_genero.genero}' adicionado ao álbum {id} com sucesso."}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/musicas/por-compositor/{nome_compositor}", tags=["Queries do Trabalho"])
async def listar_musicas_por_compositor(nome_compositor: str):
    pipeline = [
        {
            "$unwind": "$faixas"
        },
        {
            "$match": {
                "faixas.compositores": nome_compositor
            }
        },
        {
            "$project": {
                "_id": 0,
                "titulo_musica": "$faixas.titulo",
                "album": "$titulo",
                "artista": "$artista",
                "todos_compositores": "$faixas.compositores"
            }
        }
    ]
    
    try:
        resultados = list(collection.aggregate(pipeline))
        if not resultados:
            raise HTTPException(
                status_code=404, 
                detail=f"Nenhuma música encontrada para o compositor: '{nome_compositor}'"
            )
        return resultados
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/musicas/por-compositor-exclusivo/{nome_compositor}", tags=["Queries do Trabalho"])
async def listar_musicas_por_compositor_exclusivo(nome_compositor: str):
    pipeline = [
        {
            "$unwind": "$faixas"
        },
        {
            "$match": {
                "faixas.compositores": [nome_compositor]
            }
        },
        {
            "$project": {
                "_id": 0,
                "titulo_musica": "$faixas.titulo",
                "album": "$titulo",
                "artista": "$artista"
            }
        }
    ]
    
    try:
        resultados = list(collection.aggregate(pipeline))
        if not resultados:
            raise HTTPException(
                status_code=404, 
                detail=f"Nenhuma música encontrada composta exclusivamente por: '{nome_compositor}'"
            )
        return resultados
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/musicas/compositor", tags=["Queries do Trabalho"])
async def corrigir_nome_compositor(update_data: UpdateCompositorNome):
    try:
        filtro = { "faixas.compositores": update_data.nome_antigo }

        operacao_update = {
            "$set": { "faixas.$[elem].compositores.$[comp]": update_data.nome_novo }
        }

        filtros_de_array = [
            { "elem.compositores": update_data.nome_antigo },
            { "comp": update_data.nome_antigo }
        ]

        resultado = collection.update_many(
            filtro,
            operacao_update,
            array_filters=filtros_de_array
        )
        
        if resultado.matched_count == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"Nenhum álbum encontrado com o compositor '{update_data.nome_antigo}'."
            )

        return {
            "message": "Operação de correção de nome concluída.",
            "albuns_encontrados": resultado.matched_count,
            "albuns_modificados": resultado.modified_count
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/musicas/mais-longa", tags=["Queries do Trabalho"])
async def encontrar_musica_mais_longa():
    pipeline = [
        {
            "$unwind": "$faixas"
        },
        {
            "$sort": { "faixas.duracao_segundos": -1 }
        },
        {
            "$limit": 1
        },
        {
            "$project": {
                "_id": 0,
                "titulo_musica": "$faixas.titulo",
                "duracao_em_segundos": "$faixas.duracao_segundos",
                "album": "$titulo",
                "artista": "$artista"
            }
        }
    ]

    try:
        resultado = list(collection.aggregate(pipeline))
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Nenhuma música encontrada na coleção.")
            
        return resultado[0]
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/albuns/por-compositor/{nome_compositor}", tags=["Queries do Trabalho"])
async def remover_album_por_compositor(nome_compositor: str):
    try:
        filtro = { "faixas.compositores": nome_compositor }

        resultado = collection.delete_many(filtro)

        if resultado.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum álbum encontrado com o compositor '{nome_compositor}' para remover."
            )

        return {
            "message": f"Operação de exclusão por compositor '{nome_compositor}' concluída.",
            "documentos_removidos": resultado.deleted_count
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artistas/media-faixas-por-disco", tags=["Queries do Trabalho"])
async def calcular_media_faixas_por_artista():
    pipeline = [
        {
            "$addFields": {
                "numeroDeFaixas": { "$size": "$faixas" }
            }
        },
        {
            "$group": {
                "_id": "$artista",
                "totalDiscos": { "$sum": 1 },
                "mediaFaixas": { "$avg": "$numeroDeFaixas" }
            }
        },
        {
            "$project": {
                "_id": 0,
                "artista": "$_id",
                "totalDiscos": "$totalDiscos",
                "mediaDeFaixasPorDisco": "$mediaFaixas"
            }
        },
        {
            "$sort": { "totalDiscos": -1 }
        }
    ]
    
    try:
        resultados = list(collection.aggregate(pipeline))
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/albuns/remover-ultima-faixa/por-compositor/{nome_compositor}", tags=["Queries do Trabalho"])
async def remover_ultima_faixa_por_compositor(nome_compositor: str):
    try:
        filtro = {
            "$expr": {
                "$let": {
                    "vars": {
                        "ultima_faixa": { "$arrayElemAt": ["$faixas", -1] }
                    },
                    "in": {
                        "$in": [ nome_compositor, "$$ultima_faixa.compositores" ]
                    }
                }
            }
        }
        
        operacao_update = {
            "$pop": { "faixas": 1 }
        }

        resultado = collection.update_many(
            filtro,
            operacao_update
        )

        if resultado.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum álbum encontrado cuja última faixa tenha sido composta por '{nome_compositor}'."
            )

        return {
            "message": f"Operação concluída. Última faixa removida dos álbuns correspondentes.",
            "albuns_modificados": resultado.modified_count
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/albuns", status_code=201, tags=["CRUD Básico"])
async def adicionar_album(album: Album):
    try:
        album_dict = album.model_dump(by_alias=True)
        album_dict.pop("id", None)
        result = collection.insert_one(album_dict)
        return {"id_inserido": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/albuns", response_model=List[Album], tags=["CRUD Básico"])
async def listar_albuns():
    albuns_list = []
    cursor = collection.find({})
    for documento in cursor:
        documento["_id"] = str(documento["_id"])
        albuns_list.append(Album(**documento))
    return albuns_list

@router.get("/albuns/{id}", response_model=Album, tags=["CRUD Básico"])
async def buscar_album_por_id(id: str):
    try:
        documento = collection.find_one({"_id": ObjectId(id)})
        if documento:
            documento["_id"] = str(documento["_id"])
            return Album(**documento)
        raise HTTPException(status_code=404, detail=f"Álbum com id {id} não encontrado.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"ID inválido ou álbum não encontrado: {e}")