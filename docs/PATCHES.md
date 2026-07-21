# Patches

## TimelineCursor compatibility

### Problema

X modificó la estructura del cursor utilizado en las respuestas de Timeline.

Formato antiguo:

```json
{
  "content": {
    "itemContent": {
      "value": "..."
    }
  }
}
```

Formato nuevo:

```json
{
  "content": {
    "value": "..."
    }
}
```

El código original asumía únicamente el formato antiguo:

```python
entry["content"]["itemContent"]["value"]
```

Esto provocaba:

```
KeyError: 'itemContent'
```

al consultar ciertos tweets, especialmente artículos largos.

---

## Solución

Se agregó el método privado:

```python
Client._extract_cursor_value()
```

que intenta obtener el cursor utilizando ambos formatos.

Primero:

```
content.itemContent.value
```

Si no existe:

```
content.value
```

De esta manera el comportamiento es compatible con ambos formatos sin romper versiones anteriores.

---

## Archivos modificados

```
twikit/client/client.py
```

---

## Compatibilidad

✔ Formato antiguo

✔ Formato nuevo

✔ Compatible hacia atrás

---

## Estado

Probado exitosamente utilizando:

```
client.get_tweet_by_id(tweet_id)
```

con artículos largos de X que anteriormente generaban:

```
KeyError: 'itemContent'
```
