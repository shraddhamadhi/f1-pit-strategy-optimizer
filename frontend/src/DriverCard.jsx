const DriverCard = ({ name, nationality, number, team, color, image, total, podiums, wins, wdcs }) => {
  return (
    <div style={{
      width: '340px',
      height: '480px',
      position: 'relative',
      borderRadius: '4px',
      background: `linear-gradient(165deg, ${color} 0%, #f5f7f6 70%)`,
      border: '8px solid #fff',
      boxShadow: '0 1px 1px rgba(0,0,0,0.08)',
      fontFamily: "'Inter', sans-serif",
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* NAME BAR — top of card */}
      <div style={{
        padding: '14px 18px 12px',
        backgroundColor: '#13151a',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div>
          <h2 style={{
            margin: 0,
            fontFamily: "'Oswald', sans-serif",
            fontStyle: 'italic',
            fontWeight: '600',
            fontSize: '21px',
            letterSpacing: '0.5px',
            color: '#fff',
            textTransform: 'uppercase',
            lineHeight: '1',
          }}>
            {name}
          </h2>
          <div style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: '11px',
            color: color,
            fontWeight: '600',
            letterSpacing: '1px',
            textTransform: 'uppercase',
            marginTop: '5px',
            lineHeight: '1',
          }}>
            {team} — {nationality}
          </div>
        </div>
        <div style={{
          fontFamily: "'Oswald', sans-serif",
          fontStyle: 'italic',
          fontWeight: '700',
          fontSize: '24px',
          color: '#fff',
          letterSpacing: '-1px',
          lineHeight: '1',
        }}>
          {number}
        </div>
      </div>

      {/* PHOTO */}
      <div style={{
        width: '100%',
        height: '170px',
        overflow: 'hidden',
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <img
          src={image}
          alt={name}
          style={{
            width: '100%',
            height: '100%',
            display: 'block',
            objectFit: 'contain',
          }}
        />
      </div>

      {/* STATS — fills remaining space */}
      <div style={{ padding: '12px 18px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        {[
          { label: 'Races', value: total },
          { label: 'Podiums', value: podiums },
          { label: 'Wins', value: wins },
          { label: 'WDCs', value: wdcs },
        ].map((stat, i) => (
          <div key={stat.label} style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'baseline',
            padding: '7px 0',
            borderBottom: i < 3 ? '1px solid rgba(0,0,0,0.1)' : 'none',
          }}>
            <span style={{
              fontSize: '12px',
              fontWeight: '600',
              letterSpacing: '1.2px',
              textTransform: 'uppercase',
              color: '#444',
            }}>
              {stat.label}
            </span>
            <span style={{
              fontFamily: "'Oswald', sans-serif",
              fontStyle: 'italic',
              fontSize: '19px',
              fontWeight: '600',
              color: '#13151a',
            }}>
              {stat.value}
            </span>
          </div>
        ))}
      </div>

      {/* FOOTER */}
      <div style={{
        textAlign: 'center',
        fontFamily: "'Oswald', sans-serif",
        fontSize: '11px',
        fontWeight: '500',
        letterSpacing: '2px',
        color: '#ffffff',
        textTransform: 'uppercase',
        backgroundColor: '#13151a',
        padding: '10px 0',
        flexShrink: 0,
      }}>
        Formula 1 2026
      </div>
    </div>
  )
}

export default DriverCard